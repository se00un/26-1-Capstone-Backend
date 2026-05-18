from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.schemas.trip import TripCreate, TripResponse, TripMyResponse, InvitationRequest, InvitationResponse
from app.services import trip_service
from app.crud import trip as trip_crud
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=TripResponse, status_code=201)
def create_trip(trip_in: TripCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """새로운 여행 생성"""
    return trip_service.create_new_trip(db=db, trip_in=trip_in, current_user_id=current_user.id)

@router.get("/my", response_model=List[TripMyResponse])
def get_my_trips(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """내가 참여 중인 전체 여행 목록 조회"""
    return trip_service.get_my_trips(db=db, current_user_id=current_user.id)

@router.post("/{trip_id}/invites", response_model=InvitationResponse, status_code=201)
def create_invite(trip_id: int, invite_in: InvitationRequest = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """특정 여행의 초대 코드 생성 (Owner/Editor 전용)"""
    expires_at = invite_in.expires_at if invite_in else None
    return trip_service.generate_invite(db=db, trip_id=trip_id, current_user_id=current_user.id, expires_at=expires_at)

@router.delete("/{trip_id}")
def delete_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """여행 삭제 (Owner 전용)"""
    # 여행 존재 여부 확인
    trip = trip_crud.get_trip_by_id(db, trip_id)
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

    # Owner 권한 확인
    if trip.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the owner can delete this trip")

    trip_crud.delete_trip(db, trip_id)
    return {"message": "Trip deleted successfully"}
