from fastapi import FastAPI
from app.api.router import api_router
from app.core.config import settings

# DB 세팅 (Alembic 없이 서버 켤 때 모든 테이블 자동 생성)
from app.db.database import engine
from app.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Trip-log API",
    description="Trip-log Backend API with FastAPI"
)

# API 라우터 등록
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.get("/")
def read_root():
    return {"message": "Welcome to Trip-log API Server!"}
