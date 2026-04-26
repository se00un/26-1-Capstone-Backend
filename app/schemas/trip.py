from pydantic import BaseModel
from typing import Optional
from datetime import date as Date, datetime

# --- Trip Schemas ---
class TripBase(BaseModel):
    title: str
    representative_lat: float
    representative_lng: float
    is_group_trip: Optional[bool] = False
    
class TripCreate(TripBase):
    start_date: Date
    end_date: Date

class TripResponse(TripBase):
    id: int
    owner_id: int
    status: str
    start_date: Date
    end_date: Date
    created_at: datetime

    class Config:
        from_attributes = True

# --- Trip Member Schemas ---
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

# --- Invitation Schemas ---
class InvitationBase(BaseModel):
    trip_id: int
    invite_code: str
    invited_by: int
    status: Optional[str] = "pending"
    expires_at: Optional[datetime] = None

class InvitationCreate(InvitationBase):
    pass

class InvitationResponse(InvitationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
