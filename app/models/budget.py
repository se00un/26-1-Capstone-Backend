from sqlalchemy import Column, String, DateTime, BigInteger, ForeignKey, func, Numeric, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
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
    amount_krw = Column(Numeric)
    expense_date = Column(Date, nullable=False)
    memo = Column(Text)
    receipt_id = Column(BigInteger, ForeignKey("receipts.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    trip = relationship("Trip", back_populates="expenses")
    creator = relationship("User", back_populates="expenses")
    receipt = relationship("Receipt", back_populates="expenses")
    splits = relationship("ExpenseSplit", back_populates="expense")

class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    trip_id = Column(BigInteger, ForeignKey("trips.id"))
    uploaded_by = Column(BigInteger, ForeignKey("users.id"))
    image_url = Column(Text, nullable=False)
    raw_ocr_text = Column(Text)
    parsed_json = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    trip = relationship("Trip", back_populates="receipts")
    uploader = relationship("User", back_populates="uploaded_receipts")
    expenses = relationship("Expense", back_populates="receipt")

class ExpenseSplit(Base):
    __tablename__ = "expense_splits"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    expense_id = Column(BigInteger, ForeignKey("expenses.id"))
    user_id = Column(BigInteger, ForeignKey("users.id"))
    split_amount = Column(Numeric, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    expense = relationship("Expense", back_populates="splits")
    user = relationship("User", back_populates="expense_splits")
