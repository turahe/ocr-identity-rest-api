import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, BigInteger, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from .base import Base


class Media(Base):
    """Media model for file storage with polymorphic relationships"""
    
    __tablename__ = "media"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    hash = Column(String(255), nullable=True)
    file_name = Column(String(255), nullable=False)
    disk = Column(String(255), nullable=False)
    mime_type = Column(String(255), nullable=False)
    size = Column(Integer, nullable=False)
    record_left = Column(BigInteger, nullable=True)
    record_right = Column(BigInteger, nullable=True)
    record_dept = Column(BigInteger, nullable=True)
    record_ordering = Column(BigInteger, nullable=True)
    parent_id = Column(PostgresUUID(as_uuid=True), ForeignKey("media.id"), nullable=True)
    custom_attribute = Column(String(255), nullable=True)
    created_by = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    deleted_by = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Self-referencing relationships
    parent = relationship("Media", backref="children", remote_side=[id])
    
    # User relationships
    creator = relationship("User", backref="created_media", foreign_keys=[created_by])
    updater = relationship("User", backref="updated_media", foreign_keys=[updated_by])
    deleter = relationship("User", backref="deleted_media", foreign_keys=[deleted_by])
    
    # Polymorphic relationships through Mediable
    mediables = relationship("Mediable", back_populates="media", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Media(id={self.id}, name='{self.name}', file_name='{self.file_name}')>"
    
    @property
    def polymorphic_relationships(self):
        """Get all polymorphic relationships"""
        relationships = {}
        for mediable in self.mediables:
            if mediable.mediable_type not in relationships:
                relationships[mediable.mediable_type] = []
            relationships[mediable.mediable_type].append(mediable)
        return relationships 