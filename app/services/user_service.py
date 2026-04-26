from sqlalchemy.orm import Session
from app.crud import user as crud_user
from app.schemas.user import UserCreate

def register_user(db: Session, user_in: UserCreate):
    existing_user = crud_user.get_user_by_email(db, email=user_in.email)
    if existing_user:
        return existing_user
    return crud_user.create_user(db=db, user=user_in)
