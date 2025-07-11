import uuid
from datetime import date
from sqlalchemy import Column, String, Date, Integer, CheckConstraint, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from .base import Base
from .people_addresses import PeopleAddress


class People(Base):
    """People model for storing personal identity information"""
    
    __tablename__ = "people"
    
    # Primary key with UUID
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Personal information
    full_name = Column(String(255), nullable=False)
    place_of_birth = Column(String(255), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    
    # Demographics
    gender = Column(String(30), nullable=False, default='UNDEFINED')
    religion = Column(String(30), nullable=False, default='UNDEFINED')
    ethnicity = Column(String(255), nullable=True)
    blood_type = Column(String(255), nullable=True)
    
    # Citizenship and nationality
    citizenship_identity = Column(String(255), nullable=False)
    citizenship = Column(String(30), nullable=False, default='UNDEFINED')
    nationality = Column(String(255), nullable=False, default='UNDEFINED')
    
    # Personal status
    marital_status = Column(String(30), nullable=False, default='UNDEFINED')
    disability_status = Column(Integer, nullable=False, default=0)
    job = Column(String(255), nullable=True)
    
    # Audit fields with UUID foreign keys
    created_by = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    deleted_by = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by], backref="created_people")
    updater = relationship("User", foreign_keys=[updated_by], backref="updated_people")
    deleter = relationship("User", foreign_keys=[deleted_by], backref="deleted_people")

    addresses = relationship("PeopleAddress", back_populates="person", cascade="all, delete-orphan")

    media = relationship("Media", back_populates="person", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "gender IN ('MALE', 'FEMALE', 'UNDEFINED')",
            name='check_gender_valid'
        ),
        CheckConstraint(
            "religion IN ('HINDU', 'BUDDHA', 'MUSLIM', 'CHRISTIAN', 'CATHOLIC', 'CONFUCIUS', 'UNDEFINED')",
            name='check_religion_valid'
        ),
        CheckConstraint(
            "citizenship IN ('INDONESIAN_CITIZEN', 'INDONESIAN_DESCENT_CITIZEN', 'ORIGINAL_INDONESIAN_CITIZEN', 'DUAL_INDONESIAN_CITIZEN', 'STATELESS_INDONESIAN_CITIZEN', 'UNDEFINED')",
            name='check_citizenship_valid'
        ),
        CheckConstraint(
            "marital_status IN ('SINGLE', 'MARRIED', 'DIVORCED', 'SEPARATED', 'WIDOWED', 'ANNULLED', 'CIVIL_DOMESTIC_PARTNERSHIP', 'COMMON_LOW_MARRIAGE', 'ENGAGED', 'COMPLICATED', 'UNDEFINED')",
            name='check_marital_status_valid'
        ),
        CheckConstraint(
            "disability_status > 0",
            name='check_disability_status_positive'
        ),
    )
    
    def __repr__(self) -> str:
        return f"<People(id={self.id}, full_name='{self.full_name}')>"
    
    def to_dict(self) -> dict:
        """Convert model to dictionary with proper date handling"""
        data = super().to_dict()
        if hasattr(self, 'date_of_birth') and self.date_of_birth is not None:
            data['date_of_birth'] = self.date_of_birth.isoformat()
        return data 


# Add relationship to People
People.addresses = relationship(
    "PeopleAddress",
    back_populates="person",
    cascade="all, delete-orphan"
) 