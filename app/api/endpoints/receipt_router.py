from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from datetime import datetime

from app.db.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services import receipt_service
from app.crud import receipt as receipt_crud


router = APIRouter()

# File upload constraints
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png"]


@router.post("/{trip_id}/upload", status_code=202)
async def upload_receipt(
    trip_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    영수증 이미지 업로드 및 OCR 분석 시작
    
    - Uploads receipt image
    - Triggers OCR processing
    - Stores receipt record with parsing results
    
    Response (202 Accepted):
    - id: Receipt ID
    - trip_id: Trip ID
    - image_url: URL to stored image
    - parsed_json: OCR extracted data
    """
    
    # Validate content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미지 파일만 업로드 가능합니다 (jpeg, png)"
        )
    
    # Read and validate file size
    image_bytes = await file.read()
    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="파일 크기는 5MB 이하여야 합니다"
        )
    
    # Upload to GCP Storage and use the public URL
    image_url = receipt_service.upload_receipt_image_to_gcs(
        file_bytes=image_bytes,
        trip_id=trip_id,
        user_id=current_user.id,
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream"
    )
    
    # Create pending receipt record
    result = receipt_service.create_pending_receipt(
        db=db,
        trip_id=trip_id,
        user_id=current_user.id,
        image_url=image_url
    )
    
    # Add OCR processing to background tasks
    background_tasks.add_task(
        receipt_service.background_process_receipt,
        result["id"],
        image_bytes
    )
    
    return {
        "id": result["id"],
        "trip_id": result["trip_id"],
        "image_url": result["image_url"],
        "status": result["status"]
    }


@router.get("/{trip_id}")
def get_receipts(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    OCR 분석 결과(JSON) 조회 - 사용자 검수 단계
    
    Get all receipts for a trip (with OCR analysis results)
    
    Response (200 OK):
    - List of receipts with:
      - id: Receipt ID
      - status: "completed" or "processing"
      - image_url: Image URL
      - parsed_json: OCR extracted data
      - raw_ocr_text: Raw OCR text
      - created_at: Creation timestamp
    """
    receipts = receipt_service.get_trip_receipts(db, trip_id)
    return receipts


@router.get("/{receipt_id}/detail")
def get_receipt_detail(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    특정 영수증 조회 (검수 단계)
    
    Get specific receipt for review before confirming as expense
    """
    result = receipt_service.get_receipt_for_review(db, receipt_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found"
        )
    
    return result


@router.post("/{receipt_id}/confirm-receipt", status_code=201)
def confirm_receipt(
    receipt_id: int,
    expense_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    사용자가 업로드하여 파싱된 OCR 데이터를 Expense로 최종 확정
    
    Convert confirmed receipt to Expense record
    
    Request Body:
    - expense_type: "shared" or "personal"
    - title: Expense title
    - category: Expense category
    - amount_original: Original amount
    - currency: Currency code (KRW, USD, etc.)
    - amount_krw: Amount in KRW
    - expense_date: Expense date (YYYY-MM-DD)
    - memo: Optional memo
    - created_by: User ID who created this
    
    Response (201 Created):
    - Full Expense record with receipt_id mapping
    """
    
    # Verify receipt exists
    db_receipt = receipt_crud.get_receipt_by_id(db, receipt_id)
    if not db_receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found"
        )
    
    # Ensure user created this receipt or is trip admin
    if db_receipt.uploaded_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to confirm this receipt"
        )
    
    # Ensure expense_data has required fields
    if "trip_id" not in expense_data:
        expense_data["trip_id"] = db_receipt.trip_id
    
    if "created_by" not in expense_data:
        expense_data["created_by"] = current_user.id
    
    # Confirm receipt as expense
    result = receipt_service.confirm_receipt_as_expense(
        db,
        receipt_id,
        expense_data
    )
    
    if result and "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return result


@router.delete("/{receipt_id}")
def delete_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete receipt (only if not yet converted to expense)
    """
    
    # Verify receipt exists
    db_receipt = receipt_crud.get_receipt_by_id(db, receipt_id)
    if not db_receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found"
        )
    
    # Ensure user uploaded this receipt
    if db_receipt.uploaded_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this receipt"
        )
    
    # Try to delete
    success = receipt_service.delete_receipt(db, receipt_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete receipt - already associated with an expense"
        )
    
    return {"message": "Receipt deleted successfully"}
