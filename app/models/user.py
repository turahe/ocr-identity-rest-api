import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from .base import Base


class User(Base):
    """User model for authentication and user management"""
    
    __tablename__ = "users"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    phone = Column(String(20), unique=True, nullable=True, index=True)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    phone_verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    created_by = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=datetime.utcnow, nullable=False)
    
    # Self-referencing relationships
    created_users = relationship("User", backref="creator", remote_side=[id], foreign_keys=[created_by])
    deleted_users = relationship("User", backref="deleter", remote_side=[id], foreign_keys=[deleted_by])
    
    # Other relationships
    identity_documents = relationship("IdentityDocument", back_populates="user", cascade="all, delete-orphan")
    ocr_jobs = relationship("OCRJob", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    
    # Polymorphic media relationships
    media_relationships = relationship("Mediable", 
                                    primaryjoin="and_(User.id==Mediable.mediable_id, "
                                               "Mediable.mediable_type=='User')",
                                    cascade="all, delete-orphan")
    
    @property
    def media(self):
        """Get all media associated with this user"""
        return [rel.media for rel in self.media_relationships]
    
    def get_media_by_group(self, group: str):
        """Get media by group"""
        return [rel.media for rel in self.media_relationships if rel.group == group]
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>" 