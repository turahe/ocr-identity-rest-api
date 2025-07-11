from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class MediaRead(BaseModel):
    id: UUID
    name: str
    file_name: str
    disk: str
    mime_type: str
    size: int
    hash: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True 