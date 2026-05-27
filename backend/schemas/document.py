from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    content_type: str
    file_size: int
    text_length: int
    chunk_count: int
    uploaded_by_id: int
    created_at: datetime
