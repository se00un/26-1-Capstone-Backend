from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Trip-log"
    API_PREFIX: str = "/api"
    
    # DB Configuration
    # 기본값을 지정하지 않으면 Pydantic이 .env 파일에서 DATABASE_URL 값을 찾아 자동으로 주입합니다.
    DATABASE_URL: str
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
