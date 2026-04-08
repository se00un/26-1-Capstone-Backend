from fastapi import FastAPI
from app.api.router import api_router
from app.core.config import settings

app = FastAPI(
    title="Trip-log API",
    description="Trip-log Backend API with FastAPI"
)

# API 라우터 등록
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.get("/")
def read_root():
    return {"message": "Welcome to Trip-log API Server!"}
