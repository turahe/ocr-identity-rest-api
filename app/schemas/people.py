from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime
from app.schemas.people_addresses import PeopleAddressRead
from app.schemas.media import MediaRead

class PeopleBase(BaseModel):
    full_name: str = Field(..., max_length=255)
    place_of_birth: Optional[str] = Field(None, max_length=255)
    date_of_birth: Optional[date]
    gender: str = Field(..., max_length=30)
    religion: str = Field(..., max_length=30)
    citizenship_identity: str = Field(..., max_length=255)
    citizenship: str = Field(..., max_length=30)
    nationality: str = Field(..., max_length=255)
    ethnicity: Optional[str] = Field(None, max_length=255)
    marital_status: str = Field(..., max_length=30)
    disability_status: int = 0
    blood_type: Optional[str] = Field(None, max_length=255)
    job: Optional[str] = Field(None, max_length=255)

class PeopleCreate(PeopleBase):
    pass

class PeopleUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255)
    place_of_birth: Optional[str] = Field(None, max_length=255)
    date_of_birth: Optional[date]
    gender: Optional[str] = Field(None, max_length=30)
    religion: Optional[str] = Field(None, max_length=30)
    citizenship_identity: Optional[str] = Field(None, max_length=255)
    citizenship: Optional[str] = Field(None, max_length=30)
    nationality: Optional[str] = Field(None, max_length=255)
    ethnicity: Optional[str] = Field(None, max_length=255)
    marital_status: Optional[str] = Field(None, max_length=30)
    disability_status: Optional[int]
    blood_type: Optional[str] = Field(None, max_length=255)
    job: Optional[str] = Field(None, max_length=255)

class PeopleRead(PeopleBase):
    id: UUID
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
    deleted_by: Optional[UUID]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]
    addresses: List[PeopleAddressRead] = []
    media: List[MediaRead] = []

    class Config:
        orm_mode = True 