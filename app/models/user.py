from sqlalchemy import Column, Integer, String, DateTime, func, BigInteger
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    nickname = Column(String(100), nullable=False)
    profile_image_url = Column(String)
    provider = Column(String(50), nullable=False)
    provider_id = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 기초 뼈대: 관계 설정, 기타 필드 추가 필요
