import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, JSONB
from sqlalchemy.orm import relationship
from .base import Base


class OCRJob(Base):
    """OCR job model for tracking document processing jobs"""
    
    __tablename__ = "ocr_jobs"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(PostgresUUID(as_uuid=True), ForeignKey("identity_documents.id", ondelete="CASCADE"), nullable=False)
    job_status = Column(String(50), default="pending", nullable=False)  # 'pending', 'processing', 'completed', 'failed'
    input_file_path = Column(String(500), nullable=True)
    output_data = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="ocr_jobs")
    document = relationship("IdentityDocument", back_populates="ocr_jobs")
    
    def __repr__(self) -> str:
        return f"<OCRJob(id={self.id}, status='{self.job_status}')>" 