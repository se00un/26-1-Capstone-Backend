from sqlalchemy.orm import Session
from app.models.route import Route, RoutePlace
from app.schemas.route import RoutePlaceCreate, RoutePlaceOrder, RouteCreate
from typing import List

def get_routes_by_trip(db: Session, trip_id: int):
    return db.query(Route).filter(Route.trip_id == trip_id).all()

def create_route(db: Session, route_in: RouteCreate, current_user_id: int):
    db_route = Route(
        trip_id=route_in.trip_id,
        title=route_in.title,
        created_by=current_user_id
    )
    db.add(db_route)
    db.commit()
    db.refresh(db_route)
    return db_route

def get_route(db: Session, route_id: int):
    return db.query(Route).filter(Route.id == route_id).first()

def add_place_to_route(db: Session, route_id: int, place_data: RoutePlaceCreate):
    db_place = RoutePlace(
        route_id=route_id,
        place_name=place_data.place_name,
        country=place_data.country,
        city=place_data.city,
        address=place_data.address,
        latitude=place_data.latitude,
        longitude=place_data.longitude,
        place_type=place_data.place_type,
        visit_order=place_data.visit_order,
        memo=place_data.memo,
        visited_at=place_data.visited_at
    )
    db.add(db_place)
    db.commit()
    db.refresh(db_place)
    return db_place

def update_route_place_orders(db: Session, route_id: int, orders: List[RoutePlaceOrder]):
    # orders is a list of RoutePlaceOrder
    # First, let's verify these places belong to the route
    place_ids = [order.place_id for order in orders]
    places = db.query(RoutePlace).filter(RoutePlace.route_id == route_id, RoutePlace.id.in_(place_ids)).all()
    
    place_dict = {p.id: p for p in places}
    
    for order in orders:
        if order.place_id in place_dict:
            place_dict[order.place_id].visit_order = order.visit_order
            
    db.commit()
    
    return db.query(RoutePlace).filter(RoutePlace.route_id == route_id).order_by(RoutePlace.visit_order).all()

def delete_route_place(db: Session, route_id: int, place_id: int):
    db_place = db.query(RoutePlace).filter(RoutePlace.route_id == route_id, RoutePlace.id == place_id).first()
    if db_place:
        db.delete(db_place)
        db.commit()
        return True
    return False

def delete_route(db: Session, route_id: int):
    db_route = db.query(Route).filter(Route.id == route_id).first()
    if db_route:
        # Cascade delete places if not handled by relationship
        db.query(RoutePlace).filter(RoutePlace.route_id == route_id).delete()
        db.delete(db_route)
        db.commit()
        return True
    return False
