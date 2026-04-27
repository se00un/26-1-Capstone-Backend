from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class RoutePlaceOrder(BaseModel):
    place_id: int
    visit_order: int

class RoutePlaceOrderUpdate(BaseModel):
    orders: List[RoutePlaceOrder]

class RoutePlaceBase(BaseModel):
    place_name: str
    country: str
    city: str
    address: str
    latitude: float
    longitude: float
    place_type: str
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

class RouteCreate(BaseModel):
    trip_id: int
    title: str

class RouteResponse(RouteBase):
    id: int
    created_at: datetime
    places: List[RoutePlaceResponse] = []

    class Config:
        from_attributes = True
