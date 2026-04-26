from fastapi import APIRouter
from app.api.endpoints import user_router, trip_router, auth_router, invite_router

api_router = APIRouter()

api_router.include_router(auth_router.router, prefix="/auth", tags=["auth"])
api_router.include_router(user_router.router, prefix="/users", tags=["users"])
api_router.include_router(trip_router.router, prefix="/trips", tags=["trips"])
api_router.include_router(invite_router.router, prefix="/invites", tags=["invites"])
