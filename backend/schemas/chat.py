from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ChatSendRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    conversation_id: Optional[int] = Field(default=None, ge=1)


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: int
    sender: str
    content: str
    created_at: datetime


class ConversationSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class ConversationDetail(ConversationSummary):
    messages: List[MessageResponse]


class ChatSendResponse(BaseModel):
    conversation: ConversationSummary
    user_message: MessageResponse
    ai_message: MessageResponse
