import uuid
from datetime import date
from sqlalchemy import Column, String, Date, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, JSONB
from sqlalchemy.orm import relationship
from .base import Base


class IdentityDocument(Base):
    """Identity document model for storing OCR processed documents"""
    
    __tablename__ = "identity_documents"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    document_type = Column(String(100), nullable=False)  # 'passport', 'id_card', 'driver_license', etc.
    document_number = Column(String(255), nullable=True)
    issuing_country = Column(String(100), nullable=True)
    issue_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    extracted_data = Column(JSONB, nullable=True)  # Store OCR extracted data
    file_path = Column(String(500), nullable=True)  # Local file path
    s3_key = Column(String(500), nullable=True)  # S3 object key
    status = Column(String(50), default="pending", nullable=False)  # 'pending', 'verified', 'rejected'
    verification_notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="identity_documents")
    ocr_jobs = relationship("OCRJob", back_populates="document", cascade="all, delete-orphan")
    
    # Polymorphic media relationships
    media_relationships = relationship("Mediable", 
                                    primaryjoin="and_(IdentityDocument.id==Mediable.mediable_id, "
                                               "Mediable.mediable_type=='IdentityDocument')",
                                    cascade="all, delete-orphan")
    
    @property
    def media(self):
        """Get all media associated with this identity document"""
        return [rel.media for rel in self.media_relationships]
    
    def get_media_by_group(self, group: str):
        """Get media by group"""
        return [rel.media for rel in self.media_relationships if rel.group == group]
    
    def __repr__(self) -> str:
        return f"<IdentityDocument(id={self.id}, type='{self.document_type}', status='{self.status}')>" 