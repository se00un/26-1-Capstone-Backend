from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.budget import ExpenseCreate, ExpenseUpdate, ExpenseSplitRequest
from app.crud import trip as trip_crud
from app.crud import budget as budget_crud
from app.crud import user as user_crud
from app.services.exchange_service import get_exchange_rate

router = APIRouter()

@router.post("/{trip_id}", status_code=201)
def create_expense(
    trip_id: int,
    expense_in: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 권한 확인
    trip_member = trip_crud.get_trip_member(db, trip_id, current_user.id)
    if not trip_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this trip")
        
    # 환율 로직 적용
    expense_date_str = expense_in.expense_date.strftime("%Y-%m-%d")
    currency = expense_in.currency or "KRW"
    
    rate, is_fallback = get_exchange_rate(expense_date_str, currency, "KRW")
    
    amount_krw = float(expense_in.amount_original) * rate
    
    # receipt_id가 0으로 넘어올 경우 None으로 처리 (Swagger 등의 기본값 문제 해결)
    actual_receipt_id = expense_in.receipt_id if expense_in.receipt_id != 0 else None

    db_expense = budget_crud.create_expense(
        db=db,
        trip_id=trip_id,
        created_by=current_user.id,
        title=expense_in.title,
        amount_original=float(expense_in.amount_original),
        expense_date=expense_in.expense_date,
        expense_type=expense_in.expense_type or "shared",
        category=expense_in.category,
        currency=currency,
        amount_krw=amount_krw,
        memo=expense_in.memo,
        receipt_id=actual_receipt_id
    )
    
    # dict 형태로 변환 후 exchange_rate 주입
    resp = {c.name: getattr(db_expense, c.name) for c in db_expense.__table__.columns}
    resp["exchange_rate"] = rate
    return resp

@router.get("/{trip_id}")
def get_expenses(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 권한 확인
    trip_member = trip_crud.get_trip_member(db, trip_id, current_user.id)
    if not trip_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this trip")
        
    expenses = budget_crud.get_expenses_by_trip(db, trip_id)
    
    # shared + personal(본인것만)
    filtered = [
        e for e in expenses
        if e.expense_type == "shared" or (e.expense_type == "personal" and e.created_by == current_user.id)
    ]
    
    result = []
    for e in filtered:
        e_dict = {c.name: getattr(e, c.name) for c in e.__table__.columns}
        # exchange_rate 계산 (amount_original이 0이 아니면 계산, 아니면 1.0)
        orig = float(e.amount_original) if e.amount_original else 0
        krw = float(e.amount_krw) if e.amount_krw else 0
        e_dict["exchange_rate"] = (krw / orig) if orig > 0 else 1.0
        result.append(e_dict)
        
    return result

@router.delete("/{expense_id}")
def delete_expense_api(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense = budget_crud.get_expense_by_id(db, expense_id)
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
        
    if expense.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only creator can delete this expense")
        
    budget_crud.delete_expense(db, expense_id)
    return {"message": "Expense deleted successfully"}

@router.patch("/{expense_id}")
def update_expense_api(
    expense_id: int,
    expense_in: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense = budget_crud.get_expense_by_id(db, expense_id)
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
        
    if expense.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only creator can update this expense")
        
    update_data = expense_in.model_dump(exclude_unset=True)
    
    # receipt_id가 0으로 오면 None으로 처리
    if "receipt_id" in update_data and update_data["receipt_id"] == 0:
        update_data["receipt_id"] = None

    # 환율 관련 필드가 변경되었으면 amount_krw 재계산
    if "amount_original" in update_data or "currency" in update_data or "expense_date" in update_data:
        new_amount = float(update_data.get("amount_original", expense.amount_original))
        new_currency = update_data.get("currency", expense.currency) or "KRW"
        new_date = update_data.get("expense_date", expense.expense_date)
        
        rate, _ = get_exchange_rate(new_date.strftime("%Y-%m-%d"), new_currency, "KRW")
        update_data["amount_krw"] = new_amount * rate
        
    updated = budget_crud.update_expense(db, expense_id, **update_data)
    
    resp = {c.name: getattr(updated, c.name) for c in updated.__table__.columns}
    
    # 현재 환율 다시 계산하여 응답에 포함
    orig = float(updated.amount_original) if updated.amount_original else 0
    krw = float(updated.amount_krw) if updated.amount_krw else 0
    resp["exchange_rate"] = (krw / orig) if orig > 0 else 1.0
    
    return resp

@router.post("/{expense_id}/split", status_code=201)
def calculate_expense_split(
    expense_id: int,
    split_req: ExpenseSplitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense = budget_crud.get_expense_by_id(db, expense_id)
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
        
    if expense.expense_type != "shared":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can only split shared expenses")
        
    user_ids = split_req.user_ids
    if not user_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user_ids list cannot be empty")
        
    N = len(user_ids)
    total_krw = float(expense.amount_krw or 0)
    
    base_split = round(total_krw / N)
    remainder = total_krw - (base_split * N)
    
    splits = []
    for i, uid in enumerate(user_ids):
        amount = base_split
        if i == 0:
            amount += remainder
            
        # Get user info
        user = user_crud.get_user_by_id(db, uid)
        splits.append({
            "user_id": uid,
            "nickname": user.nickname if user else "Unknown",
            "split_amount": amount
        })
        
    return {
        "id": expense_id, # return expense_id as id just to match example
        "expense_id": expense_id,
        "total_amount_krw": total_krw,
        "splits": splits,
        "created_at": datetime.now().isoformat()
    }
