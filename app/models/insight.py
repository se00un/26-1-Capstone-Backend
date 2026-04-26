from sqlalchemy import Column, String, DateTime, BigInteger, ForeignKey, func, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.db.database import Base

class TripReport(Base):
    __tablename__ = "trip_reports"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    trip_id = Column(BigInteger, ForeignKey("trips.id"))
    report_text = Column(Text)
    summary_json = Column(JSONB)

    # Relationships
    trip = relationship("Trip", back_populates="trip_report")

class UserHistory(Base):
    __tablename__ = "user_history"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    spending_style = Column(String(255))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="user_history")

class RecommendationReport(Base):
    __tablename__ = "recommendation_reports"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    profile_snapshot_json = Column(JSONB)
    recommendation_text = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")
