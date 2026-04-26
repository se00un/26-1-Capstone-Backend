from sqlalchemy import Column, DateTime, BigInteger, ForeignKey, func, Numeric
from sqlalchemy.orm import relationship
from app.db.database import Base

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
