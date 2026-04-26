from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TripMemberBase(BaseModel):
    trip_id: int
    user_id: int
    role: Optional[str] = "editor"

class TripMemberCreate(TripMemberBase):
    pass

class TripMemberResponse(TripMemberBase):
    id: int
    joined_at: datetime

    class Config:
        from_attributes = True
