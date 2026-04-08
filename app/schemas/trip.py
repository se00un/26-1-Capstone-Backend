from pydantic import BaseModel
from typing import Optional

# 기초 뼈대
class TripBase(BaseModel):
    title: str
    representative_lat: float
    representative_lng: float
    
class TripCreate(TripBase):
    start_date: Date
    end_date: Date

class TripResponse(TripBase):
    id: int
    owner_id: int
    status: str

    class Config:
        from_attributes = True
