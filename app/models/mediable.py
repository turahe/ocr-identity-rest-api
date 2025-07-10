import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from .base import Base


class Mediable(Base):
    """Mediable model for polymorphic relationships between Media and other models"""
    
    __tablename__ = "mediables"
    
    media_id = Column(PostgresUUID(as_uuid=True), ForeignKey("media.id"), primary_key=True)
    mediable_id = Column(PostgresUUID(as_uuid=True), primary_key=True)
    mediable_type = Column(String(255), nullable=False)
    group = Column(String(255), nullable=False)
    
    # Relationships
    media = relationship("Media", back_populates="mediables")
    
    def __repr__(self) -> str:
        return f"<Mediable(media_id={self.media_id}, mediable_type='{self.mediable_type}', mediable_id={self.mediable_id})>"
    
    @property
    def mediable_object(self):
        """Get the related object based on mediable_type"""
        # This would be implemented based on your application's model registry
        # For now, we'll return None - you can implement this based on your needs
        return None 