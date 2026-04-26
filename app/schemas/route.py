from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class RoutePlaceBase(BaseModel):
    place_name: str
    latitude: float
    longitude: float
    visit_order: int
    memo: Optional[str] = None
    visited_at: Optional[datetime] = None

class RoutePlaceCreate(RoutePlaceBase):
    pass

class RoutePlaceResponse(RoutePlaceBase):
    id: int
    route_id: int

    class Config:
        from_attributes = True

class RouteBase(BaseModel):
    trip_id: int
    title: Optional[str] = None
    created_by: int

class RouteCreate(RouteBase):
    pass

class RouteResponse(RouteBase):
    id: int
    places: List[RoutePlaceResponse] = []

    class Config:
        from_attributes = True
