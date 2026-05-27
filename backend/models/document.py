from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from models.base import BaseModel


class UploadedDocument(BaseModel):
    __tablename__ = "uploaded_documents"

    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    text_length = Column(Integer, nullable=False, default=0)
    chunk_count = Column(Integer, nullable=False, default=0)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    uploaded_by = relationship("User", back_populates="uploaded_documents")
