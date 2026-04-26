from sqlalchemy import Column, String, DateTime, BigInteger, ForeignKey, func, Numeric, Date, Text
from sqlalchemy.orm import relationship
from app.db.database import Base

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    trip_id = Column(BigInteger, ForeignKey("trips.id"))
    created_by = Column(BigInteger, ForeignKey("users.id"))
    expense_type = Column(String(20)) # personal / shared
    title = Column(String(255), nullable=False)
    category = Column(String(100))
    amount_original = Column(Numeric, nullable=False)
    currency = Column(String(10))
    exchange_rate = Column(Numeric)
    amount_krw = Column(Numeric)
    expense_date = Column(Date, nullable=False)
    memo = Column(Text)
    receipt_id = Column(BigInteger, ForeignKey("receipts.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    trip = relationship("Trip", back_populates="expenses")
    creator = relationship("User", back_populates="expenses")
    receipt = relationship("Receipt", back_populates="expenses")
    splits = relationship("ExpenseSplit", back_populates="expense")
