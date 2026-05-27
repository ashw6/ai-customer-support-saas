"""Shared query helpers for ticket listing (pagination, filters, search, sort)."""
from __future__ import annotations

import math
from typing import Literal, Optional

from sqlalchemy import case, or_
from sqlalchemy.orm import Query

from models.ticket import Ticket
from schemas.ticket import TicketPriority, TicketStatus


def escape_ilike_pattern(value: str) -> str:
    """Escape ``%``, ``_``, and ``\\`` for use with ``ILIKE ... ESCAPE '\\'``."""
    return value.replace("\\", "\\\\").replace("%", r"\%").replace("_", r"\_")


def priority_sort_column():
    """Numeric ordering: low < medium < high."""
    return case(
        (Ticket.priority == "low", 1),
        (Ticket.priority == "medium", 2),
        (Ticket.priority == "high", 3),
        else_=0,
    )


def apply_sort(
    q: Query,
    *,
    sort_by: Literal["created_at", "priority", "urgency_score", "status"],
    order: Literal["asc", "desc"],
) -> Query:
    if sort_by == "created_at":
        col = Ticket.created_at
    elif sort_by == "priority":
        col = priority_sort_column()
    elif sort_by == "status":
        col = Ticket.status
    else:
        col = Ticket.urgency_score

    if order == "asc":
        return q.order_by(col.asc())
    return q.order_by(col.desc())


def apply_staff_filters(
    q: Query,
    *,
    status: Optional[TicketStatus] = None,
    priority: Optional[TicketPriority] = None,
    category: Optional[str] = None,
    sentiment: Optional[str] = None,
    assigned_agent_id: Optional[int] = None,
) -> Query:
    if status is not None:
        q = q.filter(Ticket.status == status.value)
    if priority is not None:
        q = q.filter(Ticket.priority == priority.value)
    if category is not None and category.strip():
        q = q.filter(Ticket.category == category.strip())
    if sentiment is not None and sentiment.strip():
        q = q.filter(Ticket.sentiment == sentiment.strip())
    if assigned_agent_id is not None:
        q = q.filter(Ticket.assigned_agent_id == assigned_agent_id)
    return q


def apply_search(q: Query, search: Optional[str]) -> Query:
    if not search or not search.strip():
        return q
    term = f"%{escape_ilike_pattern(search.strip())}%"
    return q.filter(
        or_(
            Ticket.title.ilike(term, escape="\\"),
            Ticket.description.ilike(term, escape="\\"),
        )
    )


def paginated_ticket_page(
    *,
    total: int,
    page: int,
    limit: int,
) -> tuple[int, int]:
    """Return (offset, pages)."""
    pages = math.ceil(total / limit) if limit > 0 else 0
    offset = (page - 1) * limit
    return offset, pages
