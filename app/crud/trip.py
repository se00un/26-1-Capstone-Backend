from sqlalchemy.orm import Session
from app.models.trip import Trip
from app.schemas.trip import TripCreate

# 기초 뼈대 CRUD 로직
def get_trip_by_id(db: Session, trip_id: int):
    return db.query(Trip).filter(Trip.id == trip_id).first()

def create_trip(db: Session, trip: TripCreate, owner_id: int):
    # db_trip = Trip(**trip.model_dump(), owner_id=owner_id)
    # db.add(db_trip)
    # db.commit()
    # db.refresh(db_trip)
    # return db_trip
    pass
