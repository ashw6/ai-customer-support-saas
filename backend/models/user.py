from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="customer")
    
    # Relationships
    created_tickets = relationship("Ticket", foreign_keys="Ticket.customer_id", back_populates="customer")
    assigned_tickets = relationship("Ticket", foreign_keys="Ticket.assigned_agent_id", back_populates="assigned_agent")
    conversations = relationship("Conversation", back_populates="user")
    uploaded_documents = relationship("UploadedDocument", back_populates="uploaded_by")
    leads = relationship("Lead", back_populates="captured_by")
    password_reset_tokens = relationship(
        "PasswordResetToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"
