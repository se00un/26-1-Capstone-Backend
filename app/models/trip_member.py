from sqlalchemy import Column, String, DateTime, BigInteger, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.database import Base

class TripMember(Base):
    __tablename__ = "trip_members"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    trip_id = Column(BigInteger, ForeignKey("trips.id"))
    user_id = Column(BigInteger, ForeignKey("users.id"))
    role = Column(String(20)) # owner / editor
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    trip = relationship("Trip", back_populates="members")
    user = relationship("User", back_populates="trip_memberships")
