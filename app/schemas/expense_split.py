from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class ExpenseSplitBase(BaseModel):
    expense_id: int
    user_id: int
    split_amount: Decimal

class ExpenseSplitCreate(ExpenseSplitBase):
    pass

class ExpenseSplitResponse(ExpenseSplitBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
