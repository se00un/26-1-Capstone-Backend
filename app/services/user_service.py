from sqlalchemy.orm import Session
from app.crud import user as crud_user
from app.schemas.user import UserCreate

def register_user(db: Session, user_in: UserCreate):
    existing_user = crud_user.get_user_by_email(db, email=user_in.email)
    if existing_user:
        return existing_user
    return crud_user.create_user(db=db, user=user_in)

def register_or_update_google_user(db: Session, email: str, nickname: str, provider_id: str, profile_image_url: str):
    existing_user = crud_user.get_user_by_email(db, email=email)
    if existing_user:
        # 로그인 시 프로필 사진이나 닉네임이 바뀌었다면 여기서 업데이트 로직 추가 가능
        return existing_user
    
    # 신규 등록
    new_user_data = UserCreate(
        email=email,
        nickname=nickname,
        provider="google",
        provider_id=provider_id,
        profile_image_url=profile_image_url
    )
    return crud_user.create_user(db=db, user=new_user_data)
