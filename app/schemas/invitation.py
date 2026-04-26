from pydantic import BaseModel
from typing import Optional
from datetime import datetime

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
