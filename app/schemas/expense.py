from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from datetime import date as Date
from decimal import Decimal

class ExpenseBase(BaseModel):
    trip_id: int
    created_by: int
    expense_type: Optional[str] = None
    title: str
    category: Optional[str] = None
    amount_original: Decimal
    currency: Optional[str] = None
    exchange_rate: Optional[Decimal] = None
    amount_krw: Optional[Decimal] = None
    expense_date: Date
    memo: Optional[str] = None
    receipt_id: Optional[int] = None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseResponse(ExpenseBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
