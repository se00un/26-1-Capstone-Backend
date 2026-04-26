from sqlalchemy import Column, DateTime, BigInteger, ForeignKey, func, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.db.database import Base

class TripReport(Base):
    __tablename__ = "trip_reports"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    trip_id = Column(BigInteger, ForeignKey("trips.id"))
    generated_by = Column(BigInteger, ForeignKey("users.id"))
    report_text = Column(Text)
    summary_json = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    recommendation_text = Column(Text)
    recommended_destinations_json = Column(JSONB)

    # Relationships
    trip = relationship("Trip", back_populates="trip_report")
    generator = relationship("User")
