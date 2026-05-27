from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from models.base import BaseModel


class Conversation(BaseModel):
    __tablename__ = "conversations"

    title = Column(String(200), nullable=False, default="New conversation")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )


class Message(BaseModel):
    __tablename__ = "messages"

    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    sender = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")
