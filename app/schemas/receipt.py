from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime

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
