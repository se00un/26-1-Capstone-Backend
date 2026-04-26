from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime, date as Date
from decimal import Decimal

# --- Budget Schemas ---
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

# --- Expense Schemas ---
class ExpenseBase(BaseModel):
    trip_id: int
    created_by: int
    expense_type: Optional[str] = None
    title: str
    category: Optional[str] = None
    amount_original: Decimal
    currency: Optional[str] = None
    amount_krw: Optional[Decimal] = None
    expense_date: Date
    memo: Optional[str] = None
    receipt_id: Optional[int] = None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseResponse(ExpenseBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Receipt Schemas ---
class ReceiptBase(BaseModel):
    trip_id: int
    uploaded_by: int
    image_url: str
    raw_ocr_text: Optional[str] = None
    parsed_json: Optional[Dict[str, Any]] = None

class ReceiptCreate(ReceiptBase):
    pass

class ReceiptResponse(ReceiptBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- ExpenseSplit Schemas ---
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
