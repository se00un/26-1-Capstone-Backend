from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class RecommendedDestination(BaseModel):
    destination: str
    country: str
    is_overseas: bool
    reason: str


class TripReportBase(BaseModel):
    trip_id: int
    generated_by: int
    report_text: Optional[str] = None
    summary_json: Optional[Dict[str, Any]] = None
    recommendation_text: Optional[str] = None
    recommended_destinations_json: Optional[List[RecommendedDestination]] = None


class TripReportCreate(TripReportBase):
    pass


class TripReportResponse(BaseModel):
    id: int
    trip_id: int
    generated_by: int
    report_text: Optional[str] = None
    summary_json: Optional[Dict[str, Any]] = None
    recommendation_text: Optional[str] = None
    recommended_destinations_json: Optional[List[RecommendedDestination]] = None
    created_at: datetime

    class Config:
        from_attributes = True