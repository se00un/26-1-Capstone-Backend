from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class BudgetBase(BaseModel):
    trip_id: int
    category: str
    amount: Decimal
    currency: Optional[str] = "KRW"
    amount_krw: Optional[Decimal] = None

class BudgetCreate(BudgetBase):
    pass

class BudgetResponse(BudgetBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True
