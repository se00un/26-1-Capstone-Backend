from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.schemas.route import RouteResponse, RouteCreate, RoutePlaceCreate, RoutePlaceResponse, RoutePlaceOrderUpdate
from app.crud import route as crud_route
from app.crud import trip as crud_trip
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/{trip_id}", response_model=List[RouteResponse])
def get_routes(trip_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """여행 경로(Routes) 및 방문 장소 목록 조회"""
    routes = crud_route.get_routes_by_trip(db, trip_id=trip_id)
    return routes

@router.post("/", response_model=RouteResponse, status_code=status.HTTP_201_CREATED)
def create_route(route_in: RouteCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """새로운 여행 경로(Route) 생성 (예: '1일차')"""
    db_trip = crud_trip.get_trip_by_id(db, trip_id=route_in.trip_id)
    if not db_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    return crud_route.create_route(db, route_in=route_in, current_user_id=current_user.id)

@router.post("/{route_id}/places", response_model=RoutePlaceResponse, status_code=status.HTTP_201_CREATED)
def add_place_to_route(route_id: int, place: RoutePlaceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """새로운 방문 장소 추가 (특정 Route에 종속)"""
    db_route = crud_route.get_route(db, route_id=route_id)
    if not db_route:
        raise HTTPException(status_code=404, detail="Route not found")
        
    return crud_route.add_place_to_route(db, route_id=route_id, place_data=place)

@router.patch("/{route_id}/order", response_model=List[RoutePlaceResponse], status_code=status.HTTP_200_OK)
def update_route_place_orders(route_id: int, order_update: RoutePlaceOrderUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """방문 순서(visit_order) 재배치"""
    db_route = crud_route.get_route(db, route_id=route_id)
    if not db_route:
        raise HTTPException(status_code=404, detail="Route not found")
        
    updated_places = crud_route.update_route_place_orders(db, route_id=route_id, orders=order_update.orders)
    return updated_places

@router.delete("/{route_id}/places/{place_id}", status_code=status.HTTP_200_OK)
def delete_place_from_route(route_id: int, place_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """특정 여행 경로 내의 단일 장소(Place) 삭제"""
    db_route = crud_route.get_route(db, route_id=route_id)
    if not db_route:
        raise HTTPException(status_code=404, detail="Route not found")
        
    success = crud_route.delete_route_place(db, route_id=route_id, place_id=place_id)
    if not success:
        raise HTTPException(status_code=404, detail="Place not found in this route")
        
    return {"message": "Place deleted successfully."}

@router.delete("/{route_id}", status_code=status.HTTP_200_OK)
def delete_route(route_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """특정 여행 경로(Route) 삭제"""
    db_route = crud_route.get_route(db, route_id=route_id)
    if not db_route:
        raise HTTPException(status_code=404, detail="Route not found")
        
    success = crud_route.delete_route(db, route_id=route_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete route")
        
    return {"message": "Route deleted successfully."}
