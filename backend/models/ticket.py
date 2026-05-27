from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import BaseModel

class Ticket(BaseModel):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="open")
    priority = Column(String(20), nullable=False, default="medium")
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_agent_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    sentiment = Column(String(20), nullable=True)
    ai_reply = Column(Text, nullable=True)
    is_escalated = Column(Boolean, nullable=False, default=False)
    category = Column(String(50), nullable=True)
    urgency_score = Column(Integer, nullable=False, default=1)
    sla_tag = Column(String(50), nullable=True)
    smart_labels = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    customer = relationship("User", foreign_keys=[customer_id], back_populates="created_tickets")
    assigned_agent = relationship("User", foreign_keys=[assigned_agent_id], back_populates="assigned_tickets")
    
    def __repr__(self):
        return f"<Ticket(id={self.id}, title={self.title}, status={self.status}, priority={self.priority})>"
