from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class LeadCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=7, max_length=40)
    source: str = Field(default="chat", max_length=50)
    matched_keyword: Optional[str] = Field(default=None, max_length=80)
    source_message: Optional[str] = Field(default=None, max_length=4000)

    @field_validator("name", "phone", "source")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Field cannot be blank")
        return stripped

    @field_validator("matched_keyword", "source_message")
    @classmethod
    def strip_optional_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class LeadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    phone: str
    source: str
    matched_keyword: Optional[str] = None
    source_message: Optional[str] = None
    followup_sent: bool
    captured_by_user_id: Optional[int] = None
    created_at: datetime


class LeadAnalytics(BaseModel):
    total: int
    today: int
    followups_sent: int
    conversion_rate: float


class LeadPageData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: List[LeadResponse]
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    limit: int = Field(..., ge=1)
    pages: int = Field(..., ge=0)
