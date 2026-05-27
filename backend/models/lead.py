from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from models.base import BaseModel


class Lead(BaseModel):
    __tablename__ = "leads"

    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(40), nullable=False)
    source = Column(String(50), nullable=False, default="chat")
    matched_keyword = Column(String(80), nullable=True)
    source_message = Column(Text, nullable=True)
    followup_sent = Column(Boolean, nullable=False, default=False)
    captured_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    captured_by = relationship("User", back_populates="leads")
