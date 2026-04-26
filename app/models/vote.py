from sqlalchemy import Column, String, DateTime, BigInteger, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Vote(Base):
    __tablename__ = "votes"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    trip_id = Column(BigInteger, ForeignKey("trips.id"))
    created_by = Column(BigInteger, ForeignKey("users.id"))
    title = Column(String(255), nullable=False)
    description = Column(String(255))
    status = Column(String(50), default='active')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    trip = relationship("Trip", back_populates="votes")
    options = relationship("VoteOption", back_populates="vote")
    responses = relationship("VoteResponse", back_populates="vote")

class VoteOption(Base):
    __tablename__ = "vote_options"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    vote_id = Column(BigInteger, ForeignKey("votes.id"))
    option_text = Column(String(255), nullable=False)

    # Relationships
    vote = relationship("Vote", back_populates="options")
    responses = relationship("VoteResponse", back_populates="option")

class VoteResponse(Base):
    __tablename__ = "vote_responses"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    vote_id = Column(BigInteger, ForeignKey("votes.id"))
    option_id = Column(BigInteger, ForeignKey("vote_options.id"))
    user_id = Column(BigInteger, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    vote = relationship("Vote", back_populates="responses")
    option = relationship("VoteOption", back_populates="responses")
    user = relationship("User", back_populates="vote_responses")
