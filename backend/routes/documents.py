import logging
from pathlib import PurePath

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ai.ollama_service import LocalAIError
from ai.pdf_loader import PDFLoadError, extract_pdf_text
from ai.rag_pipeline import ingest_document
from ai.vector_store import VectorStoreError, delete_document_chunks
from database.database import get_db
from models.document import UploadedDocument
from models.user import User
from schemas.document import DocumentResponse
from utils.role_dependencies import require_support_agent
from utils.roles import UserRole

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])

MAX_PDF_BYTES = 10 * 1024 * 1024


def _can_manage_document(document: UploadedDocument, user: User) -> bool:
    if document.uploaded_by_id == user.id:
        return True
    return user.role in {UserRole.ADMIN, UserRole.SUPPORT_AGENT}


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_support_agent),
):
    content_type = file.content_type or "application/octet-stream"
    filename = PurePath(file.filename or "uploaded.pdf").name
    if content_type != "application/pdf" and not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF uploads are supported")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded PDF is empty")
    if len(data) > MAX_PDF_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="PDF exceeds 10MB limit")

    document: UploadedDocument | None = None
    chunks_indexed = False
    try:
        text = extract_pdf_text(data)
        document = UploadedDocument(
            filename=filename,
            content_type=content_type,
            file_size=len(data),
            text_length=len(text),
            chunk_count=0,
            uploaded_by_id=current_user.id,
        )
        db.add(document)
        db.flush()

        chunk_count = await ingest_document(document_id=document.id, filename=document.filename, text=text)
        chunks_indexed = True
        document.chunk_count = chunk_count
        db.add(document)
        db.commit()
        db.refresh(document)
    except PDFLoadError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except LocalAIError as exc:
        db.rollback()
        logger.warning("document_embedding_error", extra={"user_id": current_user.id, "error": str(exc)})
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    except SQLAlchemyError:
        if chunks_indexed and document is not None:
            try:
                delete_document_chunks(document.id)
            except VectorStoreError:
                logger.warning("document_upload_vector_cleanup_error", extra={"document_id": document.id})
        db.rollback()
        logger.exception("document_upload_db_error", extra={"user_id": current_user.id})
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not save document")

    return document


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_support_agent),
):
    q = db.query(UploadedDocument)
    if current_user.role not in {UserRole.ADMIN, UserRole.SUPPORT_AGENT}:
        q = q.filter(UploadedDocument.uploaded_by_id == current_user.id)
    return q.order_by(UploadedDocument.created_at.desc()).all()


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_support_agent),
):
    document = db.query(UploadedDocument).filter(UploadedDocument.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    if not _can_manage_document(document, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Document access denied")

    try:
        delete_document_chunks(document_id)
        db.delete(document)
        db.commit()
    except VectorStoreError as exc:
        db.rollback()
        logger.warning("document_vector_delete_error", extra={"document_id": document_id, "error": str(exc)})
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    except SQLAlchemyError:
        db.rollback()
        logger.exception("document_delete_db_error", extra={"document_id": document_id})
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not delete document")

    return None
