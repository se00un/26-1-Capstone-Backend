from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class TripReportBase(BaseModel):
    trip_id: int
    generated_by: int
    report_text: Optional[str] = None
    summary_json: Optional[Dict[str, Any]] = None
    recommendation_text: Optional[str] = None
    recommended_destinations_json: Optional[List[Dict[str, Any]]] = None

class TripReportCreate(TripReportBase):
    pass

class TripReportResponse(TripReportBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
