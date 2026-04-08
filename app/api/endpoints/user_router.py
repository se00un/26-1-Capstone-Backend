from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services import user_service

router = APIRouter()

# API 엔드포인트 기초 뼈대
@router.post("/", response_model=UserResponse)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """새로운 사용자 생성 (뼈대 API)"""
    return user_service.register_user(db=db, user_in=user_in)

@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """사용자 조회 (뼈대 API)"""
    # TODO: user_service에서 가져오기
    pass
