from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests

from app.db.database import get_db
from app.schemas.user import GoogleAuthRequest, TokenResponse, RefreshTokenRequest, RefreshTokenResponse
from app.services import user_service
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.core.config import settings
from jose import JWTError

router = APIRouter()

@router.post("/google", response_model=TokenResponse)
def google_auth(auth_in: GoogleAuthRequest, db: Session = Depends(get_db)):
    """구글 로그인 및 JWT 발급 (개발 시 id_token='mock' 입력하면 임시 통과)"""
    token = auth_in.id_token
    
    # 1. Mock 모드 (Swagger 테스트용)
    if token == "mock":
        user_info = {
            "email": "tester@gmail.com",
            "name": "Local Tester",
            "sub": "mock_google_id_12345",
            "picture": "https://dummyimage.com/100x100"
        }
    else:
        # 2. 실제 Google Token 검증 로직
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), settings.GOOGLE_CLIENT_ID)
            user_info = {
                "email": idinfo.get("email"),
                "name": idinfo.get("name"),
                "sub": idinfo.get("sub"),
                "picture": idinfo.get("picture")
            }
        except ValueError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google ID token")

    if not user_info.get("email"):
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not provided in token")

    # DB에 사용자 등록(Upsert)
    user = user_service.register_or_update_google_user(
        db=db, 
        email=user_info["email"], 
        nickname=user_info["name"], 
        provider_id=user_info["sub"], 
        profile_image_url=user_info["picture"]
    )

    # 자체 JWT 토큰 발급
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user
    )

@router.post("/refresh", response_model=RefreshTokenResponse)
def refresh_token(request: RefreshTokenRequest):
    """리프레시 토큰으로 액세스 토큰 재발급"""
    try:
        payload = verify_token(request.refresh_token)
        user_id = payload.get("sub")
        token_type = payload.get("type")
        
        if user_id is None or token_type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token type")
            
        access_token = create_access_token(subject=user_id)
        return RefreshTokenResponse(access_token=access_token)
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
