from sqlalchemy.orm import Session
from app.crud import user as crud_user
from app.schemas.user import UserCreate

# 서비스 계층 기초 뼈대 (비즈니스 로직 작성 공간)
def register_user(db: Session, user_in: UserCreate):
    existing_user = crud_user.get_user_by_email(db, email=user_in.email)
    if existing_user:
        return existing_user # 혹은 Exception raise
    return crud_user.create_user(db=db, user=user_in)
