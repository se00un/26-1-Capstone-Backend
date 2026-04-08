from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.trip import TripCreate, TripResponse
from app.services import trip_service

router = APIRouter()

# API 엔드포인트 기초 뼈대
@router.post("/", response_model=TripResponse)
def create_trip(trip_in: TripCreate, db: Session = Depends(get_db)):
    """새로운 여행 생성 (뼈대 API)"""
    # current_user_id = dependency 로 가져오기
    # return trip_service.create_new_trip(db=db, trip_in=trip_in, current_user_id=1)
    pass
