from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# 기초 뼈대
class UserBase(BaseModel):
    email: EmailStr
    nickname: str

class UserCreate(UserBase):
    provider: str
    provider_id: str
    profile_image_url: Optional[str] = None

class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    profile_image_url: Optional[str] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    provider: str
    provider_id: str
    profile_image_url: Optional[str] = None

    class Config:
        from_attributes = True

# --- Auth Schemas ---
class GoogleAuthRequest(BaseModel):
    id_token: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserResponse

class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
