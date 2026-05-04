from pydantic_settings import BaseSettings

# render 배포용 
class Settings(BaseSettings):
    PROJECT_NAME: str = "Trip-log"
    API_PREFIX: str = "/api"
    
    # CORS Configuration
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # DB Configuration
    DATABASE_URL: str
    
    # Auth Configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    GOOGLE_CLIENT_ID: str
    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

settings = Settings()
