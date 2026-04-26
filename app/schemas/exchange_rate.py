from pydantic import BaseModel
from typing import Optional
from datetime import date as Date
from decimal import Decimal

class ExchangeRateBase(BaseModel):
    base_currency: Optional[str] = 'KRW'
    target_currency: str
    rate: Decimal
    fetched_date: Date

class ExchangeRateCreate(ExchangeRateBase):
    pass

class ExchangeRateResponse(ExchangeRateBase):
    id: int

    class Config:
        from_attributes = True
