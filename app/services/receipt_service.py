import os
from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.db.database import SessionLocal

from google.cloud import storage
from google.auth.exceptions import GoogleAuthError

from app.services.ocr_processor import ReceiptProcessor
from app.crud import receipt as receipt_crud
from app.crud import budget as budget_crud

processor = ReceiptProcessor()
gcs_client = None
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")


def upload_receipt_image_to_gcs(
    file_bytes: bytes,
    trip_id: int,
    user_id: int,
    filename: str,
    content_type: str
) -> str:
    if not GCS_BUCKET_NAME:
        raise RuntimeError("GCS_BUCKET_NAME is not configured")

    destination_blob_name = f"receipts/{trip_id}/{user_id}_{int(datetime.now().timestamp())}_{filename}"

    global gcs_client
    if gcs_client is None:
        try:
            gcs_client = storage.Client()
        except Exception as e:
            raise RuntimeError(f"GCS credentials missing or invalid: {str(e)}")

    try:
        bucket = gcs_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(file_bytes, content_type=content_type)
        return blob.public_url

    except GoogleAuthError as e:
        raise RuntimeError(f"GCS authentication failed: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"GCS upload failed: {str(e)}")



def create_pending_receipt(
    db: Session,
    trip_id: int,
    user_id: int,
    image_url: str
) -> Dict[str, Any]:
    """
    Create a pending receipt record with status 'processing'
    """
    db_receipt = receipt_crud.create_receipt(
        db=db,
        trip_id=trip_id,
        uploaded_by=user_id,
        image_url=image_url,
        raw_ocr_text=None,
        parsed_json=None
    )
    return {
        "id": db_receipt.id,
        "trip_id": db_receipt.trip_id,
        "image_url": db_receipt.image_url,
        "status": "processing"
    }

def background_process_receipt(receipt_id: int, image_bytes: bytes):
    """
    Background task to run OCR and update the receipt
    """
    # Create a fresh DB session for the background task
    db = SessionLocal()
    try:
        # Process image with OCR
        ocr_result = processor.process_receipt(image_bytes)
        
        if "error" in ocr_result:
            raw_ocr_text = ""
            parsed_json = {"error": ocr_result["error"]}
        else:
            raw_ocr_text = ocr_result.get("raw_ocr_text", "")
            parsed_json = {k: v for k, v in ocr_result.items() if k != "raw_ocr_text"}
            
        # Update receipt in DB
        receipt_crud.update_receipt(
            db=db,
            receipt_id=receipt_id,
            raw_ocr_text=raw_ocr_text,
            parsed_json=parsed_json
        )
    except Exception as e:
        # If an unexpected error occurs, mark it with error
        receipt_crud.update_receipt(
            db=db,
            receipt_id=receipt_id,
            raw_ocr_text="",
            parsed_json={"error": f"OCR processing failed: {str(e)}"}
        )
    finally:
        db.close()


def get_receipt_for_review(db: Session, receipt_id: int) -> Optional[Dict[str, Any]]:
    """
    Get receipt data for user review
    """
    db_receipt = receipt_crud.get_receipt_by_id(db, receipt_id)
    if not db_receipt:
        return None
    
    return {
        "id": db_receipt.id,
        "trip_id": db_receipt.trip_id,
        "status": "completed" if db_receipt.parsed_json else "processing",
        "image_url": db_receipt.image_url,
        "parsed_json": db_receipt.parsed_json,
        "raw_ocr_text": db_receipt.raw_ocr_text,
        "created_at": db_receipt.created_at.isoformat()
    }


def confirm_receipt_as_expense(
    db: Session,
    receipt_id: int,
    expense_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Convert receipt OCR results to an Expense record
    """
    db_receipt = receipt_crud.get_receipt_by_id(db, receipt_id)
    if not db_receipt:
        return None
    
    # Create expense from receipt data
    try:
        db_expense = budget_crud.create_expense(
            db=db,
            trip_id=expense_data.get("trip_id", db_receipt.trip_id),
            created_by=expense_data.get("created_by"),
            title=expense_data.get("title", "Receipt Expense"),
            amount_original=float(expense_data.get("amount_original", 0)),
            expense_date=expense_data.get("expense_date"),
            expense_type=expense_data.get("expense_type", "shared"),
            category=expense_data.get("category"),
            currency=expense_data.get("currency", "KRW"),
            amount_krw=float(expense_data.get("amount_krw", 0)),
            memo=expense_data.get("memo"),
            receipt_id=receipt_id
        )
        
        return {
            "id": db_expense.id,
            "trip_id": db_expense.trip_id,
            "created_by": db_expense.created_by,
            "expense_type": db_expense.expense_type,
            "title": db_expense.title,
            "category": db_expense.category,
            "amount_original": float(db_expense.amount_original),
            "currency": db_expense.currency,
            "amount_krw": float(db_expense.amount_krw) if db_expense.amount_krw else None,
            "expense_date": db_expense.expense_date.isoformat(),
            "memo": db_expense.memo,
            "receipt_id": db_expense.receipt_id,
            "created_at": db_expense.created_at.isoformat()
        }
    
    except Exception as e:
        return {"error": f"Failed to create expense from receipt: {str(e)}"}


def get_trip_receipts(db: Session, trip_id: int) -> list:
    """Get all receipts for a trip"""
    receipts = receipt_crud.get_receipts_by_trip(db, trip_id)
    return [
        {
            "id": r.id,
            "trip_id": r.trip_id,
            "status": "completed" if r.parsed_json else "processing",
            "image_url": r.image_url,
            "parsed_json": r.parsed_json,
            "raw_ocr_text": r.raw_ocr_text,
            "created_at": r.created_at.isoformat()
        }
        for r in receipts
    ]


def delete_receipt(db: Session, receipt_id: int) -> bool:
    """Delete a receipt (only if not associated with expense)"""
    return receipt_crud.delete_receipt(db, receipt_id)
