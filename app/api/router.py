from fastapi import APIRouter
from app.api.endpoints import user_router, trip_router

api_router = APIRouter()

api_router.include_router(user_router.router, prefix="/users", tags=["users"])
api_router.include_router(trip_router.router, prefix="/trips", tags=["trips"])
# 추가적인 라우터들을 여기에 등록합니다.
# api_router.include_router(finance_router.router, prefix="/finance", tags=["finance"])
