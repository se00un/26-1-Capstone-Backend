from sqlalchemy import Column, String, DateTime, BigInteger, ForeignKey, func, Numeric
from sqlalchemy.orm import relationship
from app.db.database import Base

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    trip_id = Column(BigInteger, ForeignKey("trips.id"))
    category = Column(String(100), nullable=False)
    amount = Column(Numeric, nullable=False)
    currency = Column(String(10), default='KRW')
    amount_krw = Column(Numeric)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    trip = relationship("Trip", back_populates="budgets")
