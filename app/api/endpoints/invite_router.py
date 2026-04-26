from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.trip import TripMemberResponse
from app.services import trip_service
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/{invite_code}/accept", response_model=TripMemberResponse)
def accept_invite(invite_code: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """새로운 멤버 여행 초대 승인 및 가입"""
    return trip_service.accept_invite_code(db=db, invite_code=invite_code, current_user_id=current_user.id)
