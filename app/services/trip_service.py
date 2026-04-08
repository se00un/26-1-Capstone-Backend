from sqlalchemy.orm import Session
from app.crud import trip as crud_trip
from app.schemas.trip import TripCreate

def create_new_trip(db: Session, trip_in: TripCreate, current_user_id: int):
    # 권한 확인 등 비즈니스 로직 추가
    return crud_trip.create_trip(db=db, trip=trip_in, owner_id=current_user_id)
