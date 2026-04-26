from sqlalchemy import Column, String, DateTime, func, BigInteger
from sqlalchemy.orm import relationship
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
    
    # Relationships
    trips = relationship("Trip", back_populates="owner")
    trip_memberships = relationship("TripMember", back_populates="user")
    invitations_sent = relationship("Invitation", back_populates="inviter")
    expenses = relationship("Expense", back_populates="creator")
    expense_splits = relationship("ExpenseSplit", back_populates="user")
    uploaded_receipts = relationship("Receipt", back_populates="uploader")
    created_routes = relationship("Route", back_populates="creator")
    vote_responses = relationship("VoteResponse", back_populates="user")
