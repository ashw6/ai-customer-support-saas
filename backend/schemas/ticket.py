from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10)
    priority: Optional[TicketPriority] = None


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    status: TicketStatus
    priority: TicketPriority
    customer_id: int
    assigned_agent_id: Optional[int] = None
    sentiment: Optional[str] = None
    ai_reply: Optional[str] = None
    is_escalated: bool
    category: Optional[str] = None
    urgency_score: int
    sla_tag: Optional[str] = None
    smart_labels: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TicketUpdate(BaseModel):
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None


class TicketStatusUpdate(BaseModel):
    status: TicketStatus


class TicketAssign(BaseModel):
    assigned_agent_id: int = Field(..., ge=1)
