from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services import user_service
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    """현재 로그인된 사용자 정보 조회"""
    return current_user

# (Optional) 디버깅용 일반 유저 정보 조회
@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """특정 사용자 번호로 조회 (뼈대 API)"""
    from app.crud.user import get_user_by_id
    user = get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
