from fastapi import FastAPI
from app.api.router import api_router
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware

import os

# DB 세팅 (Alembic 없이 서버 켤 때 모든 테이블 자동 생성)
from app.db.database import engine
from app.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Trip-log API",
    description="Trip-log Backend API with FastAPI"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.get("/")
def read_root():
    return {"message": "Welcome to Trip-log API Server!"}

if __name__ == "__main__":
    import uvicorn
    # Render는 내부적으로 PORT 환경 변수를 주입합니다.
    port = int(os.environ.get("PORT", 8000)) 
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)