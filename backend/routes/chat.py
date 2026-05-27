import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from ai.ollama_service import LocalAIError
from ai.rag_pipeline import generate_grounded_answer
from database.database import get_db
from models.conversation import Conversation, Message
from models.lead import Lead
from models.user import User
from schemas.chat import (
    ChatSendRequest,
    ChatSendResponse,
    ConversationDetail,
    ConversationSummary,
    MessageResponse,
)
from utils.dependencies import get_current_user
from utils.email_service import try_send_lead_followup
from utils.lead_detection import extract_lead_contact

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


def _can_view(conversation: Conversation, user: User) -> bool:
    return conversation.user_id == user.id


def _conversation_or_404(db: Session, conversation_id: int, user: User) -> Conversation:
    conversation = (
        db.query(Conversation)
        .options(joinedload(Conversation.messages))
        .filter(Conversation.id == conversation_id)
        .first()
    )
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    if not _can_view(conversation, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Conversation access denied")
    return conversation


def _title_from_message(message: str) -> str:
    title = " ".join(message.strip().split())
    return title[:80] or "New conversation"


@router.post("/send", response_model=ChatSendResponse, status_code=status.HTTP_201_CREATED)
async def send_chat_message(
    body: ChatSendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    content = body.message.strip()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message cannot be empty")

    try:
        if body.conversation_id:
            conversation = _conversation_or_404(db, body.conversation_id, current_user)
            if conversation.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the conversation owner can send messages to this conversation",
                )
        else:
            conversation = Conversation(title=_title_from_message(content), user_id=current_user.id)
            db.add(conversation)
            db.flush()

        history = list(conversation.messages)
        ai_content = await generate_grounded_answer(question=content, history=history)

        user_message = Message(
            conversation_id=conversation.id,
            sender="user",
            content=content,
        )
        ai_message = Message(
            conversation_id=conversation.id,
            sender="assistant",
            content=ai_content,
        )
        lead: Lead | None = None
        lead_contact = extract_lead_contact(content)
        if lead_contact:
            lead = Lead(
                name=lead_contact["name"] or current_user.name,
                email=lead_contact["email"],
                phone=lead_contact["phone"],
                source="chat",
                matched_keyword=lead_contact["matched_keyword"],
                source_message=content,
                captured_by_user_id=current_user.id,
                followup_sent=False,
            )

        rows_to_add = [user_message, ai_message]
        if lead is not None:
            rows_to_add.append(lead)
        db.add_all(rows_to_add)
        db.commit()
        db.refresh(conversation)
        db.refresh(user_message)
        db.refresh(ai_message)
        if lead is not None:
            db.refresh(lead)
            if await try_send_lead_followup(lead):
                lead.followup_sent = True
                db.add(lead)
                db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("chat_send_db_error", extra={"user_id": current_user.id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not send chat message",
        )
    except LocalAIError as exc:
        db.rollback()
        logger.warning("rag_chat_error", extra={"user_id": current_user.id, "error": str(exc)})
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )

    return ChatSendResponse(
        conversation=ConversationSummary.model_validate(conversation),
        user_message=MessageResponse.model_validate(user_message),
        ai_message=MessageResponse.model_validate(ai_message),
    )


@router.get("/history", response_model=list[ConversationSummary])
async def chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Conversation).filter(Conversation.user_id == current_user.id)
    return q.order_by(Conversation.created_at.desc()).limit(50).all()


@router.get("/conversation/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _conversation_or_404(db, conversation_id, current_user)
