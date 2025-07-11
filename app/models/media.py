import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, BigInteger, ForeignKey, Text, DateTime, UniqueConstraint
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
    record_left = Column(BigInteger, nullable=True, index=True)
    record_right = Column(BigInteger, nullable=True, index=True)
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
    
    __table_args__ = (
        UniqueConstraint('record_left', 'record_right', name='uq_media_nested_set'),
    )

    def add_child(self, db, child):
        """Add a child node to this media item (nested set logic, simplified)."""
        # This is a placeholder; real nested set insertions require shifting left/right values.
        child.parent_id = self.id
        child.record_dept = (self.record_dept or 0) + 1
        db.add(child)
        db.commit()
        db.refresh(child)
        return child

    def get_descendants(self, db):
        """Get all descendants of this node."""
        return db.query(Media).filter(
            Media.record_left > self.record_left,
            Media.record_right < self.record_right
        ).order_by(Media.record_left).all()

    def get_ancestors(self, db):
        """Get all ancestors of this node."""
        return db.query(Media).filter(
            Media.record_left < self.record_left,
            Media.record_right > self.record_right
        ).order_by(Media.record_left).all()
    
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