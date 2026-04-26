from sqlalchemy import Column, String, DateTime, Boolean, DECIMAL, BigInteger, func, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.db.database import Base

class Trip(Base):
    __tablename__ = "trips"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    owner_id = Column(BigInteger, ForeignKey("users.id"))
    title = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)  
    end_date = Column(Date, nullable=False)
    is_group_trip = Column(Boolean, default=False)
    status = Column(String(50), default='ongoing')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="trips")
    members = relationship("TripMember", back_populates="trip")
    invitations = relationship("Invitation", back_populates="trip")
    budgets = relationship("Budget", back_populates="trip")
    expenses = relationship("Expense", back_populates="trip")
    receipts = relationship("Receipt", back_populates="trip")
    routes = relationship("Route", back_populates="trip")
    votes = relationship("Vote", back_populates="trip")
    trip_report = relationship("TripReport", back_populates="trip", uselist=False)

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
