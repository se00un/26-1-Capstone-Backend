from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime

class TripReportBase(BaseModel):
    trip_id: int
    report_text: Optional[str] = None
    summary_json: Optional[Dict[str, Any]] = None

class TripReportCreate(TripReportBase):
    pass

class TripReportResponse(TripReportBase):
    id: int

    class Config:
        from_attributes = True

class UserHistoryBase(BaseModel):
    user_id: int
    spending_style: Optional[str] = None

class UserHistoryCreate(UserHistoryBase):
    pass

class UserHistoryResponse(UserHistoryBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True

class RecommendationReportBase(BaseModel):
    user_id: int
    profile_snapshot_json: Optional[Dict[str, Any]] = None
    recommendation_text: Optional[str] = None

class RecommendationReportCreate(RecommendationReportBase):
    pass

class RecommendationReportResponse(RecommendationReportBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
