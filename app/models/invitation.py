from sqlalchemy import Column, String, DateTime, BigInteger, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    trip_id = Column(BigInteger, ForeignKey("trips.id"))
    invite_code = Column(String(100), unique=True)
    invited_by = Column(BigInteger, ForeignKey("users.id"))
    status = Column(String(50), default='pending') # pending / accepted
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    trip = relationship("Trip", back_populates="invitations")
    inviter = relationship("User", back_populates="invitations_sent")
