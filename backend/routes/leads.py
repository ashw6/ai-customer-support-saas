import logging
from datetime import datetime, timezone
import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database.database import get_db
from models.lead import Lead
from models.user import User
from schemas.lead import LeadAnalytics, LeadCreate, LeadResponse, LeadPageData
from utils.dependencies import get_current_user
from utils.email_service import try_send_lead_followup
from utils.lead_detection import detect_lead_interest
from utils.role_dependencies import require_admin

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    body: LeadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    matched_keyword = body.matched_keyword
    if not matched_keyword and body.source_message:
        matched_keyword = detect_lead_interest(body.source_message)

    lead = Lead(
        name=body.name.strip(),
        email=str(body.email),
        phone=body.phone.strip(),
        source=body.source or "chat",
        matched_keyword=matched_keyword,
        source_message=body.source_message,
        captured_by_user_id=current_user.id,
        followup_sent=False,
    )

    try:
        db.add(lead)
        db.commit()
        db.refresh(lead)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("lead_create_db_error", extra={"user_id": current_user.id})
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not save lead")

    if await try_send_lead_followup(lead):
        try:
            lead.followup_sent = True
            db.add(lead)
            db.commit()
            db.refresh(lead)
        except SQLAlchemyError:
            db.rollback()
            logger.exception("lead_followup_status_db_error", extra={"lead_id": lead.id})

    return lead


@router.get("", response_model=LeadPageData)
async def list_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        total = db.query(Lead).count()
        leads = db.query(Lead).order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()
        page = math.floor(skip / limit) + 1
        pages = math.ceil(total / limit)
        return LeadPageData(
            items=leads,
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )
    except SQLAlchemyError:
        logger.exception("lead_list_db_error", extra={"user_id": current_user.id})
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not load leads")


@router.get("/analytics", response_model=LeadAnalytics)
async def lead_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        total = db.query(Lead).count()
        start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today = db.query(Lead).filter(Lead.created_at >= start_of_day).count()
        followups_sent = db.query(Lead).filter(Lead.followup_sent.is_(True)).count()
    except SQLAlchemyError:
        logger.exception("lead_analytics_db_error", extra={"user_id": current_user.id})
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not load lead analytics")

    conversion_rate = round((followups_sent / total) * 100, 1) if total else 0.0
    return LeadAnalytics(
        total=total,
        today=today,
        followups_sent=followups_sent,
        conversion_rate=conversion_rate,
    )
