from sqlalchemy.orm import Session
from app.models.budget import Receipt, Expense
from app.schemas.budget import ReceiptCreate
from datetime import datetime
from typing import Optional, Dict, Any


def create_receipt(
    db: Session, 
    trip_id: int, 
    uploaded_by: int, 
    image_url: str,
    raw_ocr_text: Optional[str] = None,
    parsed_json: Optional[Dict[str, Any]] = None
) -> Receipt:
    """Create a new receipt record"""
    db_receipt = Receipt(
        trip_id=trip_id,
        uploaded_by=uploaded_by,
        image_url=image_url,
        raw_ocr_text=raw_ocr_text,
        parsed_json=parsed_json
    )
    db.add(db_receipt)
    db.commit()
    db.refresh(db_receipt)
    return db_receipt


def get_receipt_by_id(db: Session, receipt_id: int) -> Optional[Receipt]:
    """Get receipt by ID"""
    return db.query(Receipt).filter(Receipt.id == receipt_id).first()


def get_receipts_by_trip(db: Session, trip_id: int) -> list:
    """Get all receipts for a specific trip"""
    return db.query(Receipt).filter(Receipt.trip_id == trip_id).all()


def get_pending_receipts(db: Session, trip_id: int) -> list:
    """Get receipts that haven't been converted to expenses yet"""
    # Receipt is pending if it doesn't have any associated expenses
    return db.query(Receipt).filter(
        Receipt.trip_id == trip_id,
        ~Receipt.expenses.any()  # No associated expenses
    ).all()


def update_receipt(
    db: Session,
    receipt_id: int,
    raw_ocr_text: Optional[str] = None,
    parsed_json: Optional[Dict[str, Any]] = None
) -> Optional[Receipt]:
    """Update receipt with OCR results"""
    db_receipt = get_receipt_by_id(db, receipt_id)
    if not db_receipt:
        return None
    
    if raw_ocr_text is not None:
        db_receipt.raw_ocr_text = raw_ocr_text
    if parsed_json is not None:
        db_receipt.parsed_json = parsed_json
    
    db.commit()
    db.refresh(db_receipt)
    return db_receipt


def delete_receipt(db: Session, receipt_id: int) -> bool:
    """Delete a receipt (only if not associated with any expense)"""
    db_receipt = get_receipt_by_id(db, receipt_id)
    if not db_receipt:
        return False
    
    # Check if receipt is associated with any expense
    if db_receipt.expenses:
        return False  # Cannot delete if already used in an expense
    
    db.delete(db_receipt)
    db.commit()
    return True


def get_receipt_with_expense(db: Session, receipt_id: int) -> Optional[Expense]:
    """Get the expense created from this receipt"""
    db_receipt = get_receipt_by_id(db, receipt_id)
    if not db_receipt or not db_receipt.expenses:
        return None
    return db_receipt.expenses[0]  # Receipt typically has one associated expense
