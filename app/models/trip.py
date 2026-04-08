from sqlalchemy import Column, Integer, String, DateTime, Boolean, DECIMAL, BigInteger, func, ForeignKey
from app.db.database import Base

class Trip(Base):
    __tablename__ = "trips"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    owner_id = Column(BigInteger, ForeignKey("users.id"))
    title = Column(String(255), nullable=False)
    representative_lat = Column(DECIMAL(10, 6), nullable=False)
    representative_lng = Column(DECIMAL(10, 6), nullable=False)
    start_date = Column(Date, nullable=False)  
    end_date = Column(Date, nullable=False)
    is_group_trip = Column(Boolean, default=False)
    status = Column(String(50), default='ongoing')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 기초 뼈대: 모델 필드 추가 및 관계 매핑 필요
