from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class VoteOptionBase(BaseModel):
    option_text: str

class VoteOptionCreate(VoteOptionBase):
    pass

class VoteOptionResponse(VoteOptionBase):
    id: int
    vote_id: int

    class Config:
        from_attributes = True

class VoteResponseBase(BaseModel):
    vote_id: int
    option_id: int
    user_id: int

class VoteResponseCreate(VoteResponseBase):
    pass

class VoteResponseResult(VoteResponseBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class VoteBase(BaseModel):
    trip_id: int
    created_by: int
    title: str
    description: Optional[str] = None
    status: Optional[str] = 'active'

class VoteCreate(VoteBase):
    pass

class VoteResponse(VoteBase):
    id: int
    created_at: datetime
    options: List[VoteOptionResponse] = []

    class Config:
        from_attributes = True
