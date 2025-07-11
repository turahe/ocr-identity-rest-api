from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class PeopleAddressRead(BaseModel):
    id: UUID
    address: str
    city: Optional[str]
    province: Optional[str]
    postal_code: Optional[str]
    country: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True 