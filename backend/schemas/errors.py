from typing import Any, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    request_id: str = Field(default="unknown")
