import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from .base import Base

class PeopleAddress(Base):
    """Model for storing addresses related to a person."""
    __tablename__ = "people_addresses"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(PostgresUUID(as_uuid=True), ForeignKey("people.id", ondelete="CASCADE"), nullable=False)
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=True)
    province = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    created_by = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    deleted_by = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    person = relationship("People", back_populates="addresses")

    def __repr__(self) -> str:
        return f"<PeopleAddress(id={self.id}, person_id={self.person_id}, address='{self.address}')>" 