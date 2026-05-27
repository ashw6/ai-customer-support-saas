import logging
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database.database import get_db
from models.ticket import Ticket
from models.user import User
from schemas.pagination import TicketListSuccessResponse, TicketPageData
from schemas.ticket import (
    TicketAssign,
    TicketCreate,
    TicketResponse,
    TicketStatus,
    TicketStatusUpdate,
    TicketPriority,
)
from utils.ai_reply import generate_auto_reply
from utils.ai_priority import predict_ticket_priority
from utils.ai_sentiment import analyze_sentiment
from utils.ai_ticket_intelligence import (
    calculate_urgency,
    detect_escalation,
    generate_sla_tag,
    generate_smart_labels,
    predict_category,
)
from utils.dependencies import get_current_user
from utils.role_dependencies import require_admin, require_support_agent
from utils.roles import UserRole
from utils.ticket_listing import (
    apply_search,
    apply_sort,
    apply_staff_filters,
    paginated_ticket_page,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["tickets"])


def _get_ticket_or_404(db: Session, ticket_id: int) -> Ticket:
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    return ticket


@router.post(
    "/tickets",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_ticket(
    body: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a ticket for the authenticated customer."""
    title_clean = body.title.strip()
    desc_clean = body.description.strip()
    if len(title_clean) < 5 or len(desc_clean) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title and description cannot be only whitespace and must meet minimum length",
        )
    if body.priority is not None:
        priority_value = body.priority.value
    else:
        priority_value = predict_ticket_priority(f"{title_clean} {desc_clean}")

    combined_text = f"{title_clean} {desc_clean}"
    sentiment_value = analyze_sentiment(combined_text)
    ai_reply_value = generate_auto_reply(combined_text)

    is_escalated = detect_escalation(combined_text)
    category_value = predict_category(combined_text)
    urgency_score = calculate_urgency(combined_text)
    sla_tag_value = generate_sla_tag(priority_value, is_escalated)
    smart_labels_value = generate_smart_labels(combined_text)

    ticket = Ticket(
        title=title_clean,
        description=desc_clean,
        priority=priority_value,
        status=TicketStatus.OPEN.value,
        customer_id=current_user.id,
        assigned_agent_id=None,
        sentiment=sentiment_value,
        ai_reply=ai_reply_value,
        is_escalated=is_escalated,
        category=category_value,
        urgency_score=urgency_score,
        sla_tag=sla_tag_value,
        smart_labels=smart_labels_value,
    )

    try:
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
    except SQLAlchemyError:
        db.rollback()
        logger.exception(
            "ticket_create_db_error",
            extra={"customer_id": current_user.id},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create ticket",
        )

    logger.info(
        "ticket_created",
        extra={
            "ticket_id": ticket.id,
            "customer_id": current_user.id,
            "priority": ticket.priority,
        },
    )

    return ticket


@router.get(
    "/tickets/my",
    response_model=TicketListSuccessResponse,
    status_code=status.HTTP_200_OK,
)
async def list_my_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    sort_by: Literal["created_at", "priority", "urgency_score", "status"] = Query("created_at"),
    order: Literal["asc", "desc"] = Query("desc"),
):
    """List support tickets for the authenticated customer (paginated)."""
    try:
        q = db.query(Ticket).filter(Ticket.customer_id == current_user.id)
        q = apply_search(q, search)
        total = q.count()
        offset, pages = paginated_ticket_page(total=total, page=page, limit=limit)
        q = apply_sort(q, sort_by=sort_by, order=order)
        rows = q.offset(offset).limit(limit).all()
    except SQLAlchemyError:
        logger.exception("list_my_tickets_db_error", extra={"user_id": current_user.id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not load tickets",
        )

    items = [TicketResponse.model_validate(t) for t in rows]
    return TicketListSuccessResponse(
        success=True,
        data=TicketPageData(
            items=items,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
        ),
    )


@router.get(
    "/tickets",
    response_model=TicketListSuccessResponse,
    status_code=status.HTTP_200_OK,
)
async def list_all_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_support_agent),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[TicketStatus] = Query(None),
    priority: Optional[TicketPriority] = Query(None),
    category: Optional[str] = Query(None),
    sentiment: Optional[str] = Query(None),
    assigned_agent_id: Optional[int] = Query(None, ge=1),
    search: Optional[str] = Query(None),
    sort_by: Literal["created_at", "priority", "urgency_score", "status"] = Query("created_at"),
    order: Literal["asc", "desc"] = Query("desc"),
):
    """List all tickets for staff (paginated, filterable)."""
    try:
        q = db.query(Ticket)
        q = apply_staff_filters(
            q,
            status=status,
            priority=priority,
            category=category,
            sentiment=sentiment,
            assigned_agent_id=assigned_agent_id,
        )
        q = apply_search(q, search)
        total = q.count()
        offset, pages = paginated_ticket_page(total=total, page=page, limit=limit)
        q = apply_sort(q, sort_by=sort_by, order=order)
        rows = q.offset(offset).limit(limit).all()
    except SQLAlchemyError:
        logger.exception("list_all_tickets_db_error", extra={"user_id": current_user.id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not load tickets",
        )

    items = [TicketResponse.model_validate(t) for t in rows]
    return TicketListSuccessResponse(
        success=True,
        data=TicketPageData(
            items=items,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
        ),
    )


@router.get(
    "/tickets/{ticket_id}",
    response_model=TicketResponse,
    status_code=status.HTTP_200_OK,
)
async def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a single ticket.
    Customers may only view their own tickets.
    Support agents and admins may view any ticket.
    """
    ticket = _get_ticket_or_404(db, ticket_id)

    if current_user.role == UserRole.CUSTOMER:
        if ticket.customer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own tickets",
            )

    return ticket


@router.patch(
    "/tickets/{ticket_id}/status",
    response_model=TicketResponse,
    status_code=status.HTTP_200_OK,
)
async def update_ticket_status(
    ticket_id: int,
    body: TicketStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_support_agent),
):
    """Update ticket status (admin and support agent only)."""
    ticket = _get_ticket_or_404(db, ticket_id)
    previous_status = ticket.status
    ticket.status = body.status.value

    try:
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
    except SQLAlchemyError:
        db.rollback()
        logger.exception(
            "ticket_status_update_db_error",
            extra={"ticket_id": ticket_id, "actor_id": current_user.id},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update ticket status",
        )

    logger.info(
        "ticket_status_updated",
        extra={
            "ticket_id": ticket.id,
            "actor_id": current_user.id,
            "previous_status": previous_status,
            "new_status": ticket.status,
        },
    )

    return ticket


@router.patch(
    "/tickets/{ticket_id}/assign",
    response_model=TicketResponse,
    status_code=status.HTTP_200_OK,
)
async def assign_ticket_agent(
    ticket_id: int,
    body: TicketAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Assign a support agent to a ticket (admin only)."""
    ticket = _get_ticket_or_404(db, ticket_id)

    agent = db.query(User).filter(User.id == body.assigned_agent_id).first()
    if agent is None or agent.role != UserRole.SUPPORT_AGENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assigned user must be an existing support_agent",
        )

    previous_assignee = ticket.assigned_agent_id
    ticket.assigned_agent_id = body.assigned_agent_id

    try:
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
    except SQLAlchemyError:
        db.rollback()
        logger.exception(
            "ticket_assign_db_error",
            extra={"ticket_id": ticket_id, "admin_id": current_user.id},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not assign ticket",
        )

    logger.info(
        "ticket_assigned",
        extra={
            "ticket_id": ticket.id,
            "admin_id": current_user.id,
            "assigned_agent_id": body.assigned_agent_id,
            "previous_assigned_agent_id": previous_assignee,
        },
    )

    return ticket
