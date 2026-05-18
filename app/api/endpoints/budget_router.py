from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.budget import BudgetUpsert, BudgetResponse
from app.services import budget_service
from app.crud import trip as trip_crud
from app.crud import budget as budget_crud

router = APIRouter()

@router.put("/{trip_id}")
def upsert_trip_budget(
    trip_id: int,
    budget_upsert: BudgetUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 권한 확인 (멤버인지 확인)
    trip_member = trip_crud.get_trip_member(db, trip_id, current_user.id)
    if not trip_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this trip")
        
    created_budgets = budget_service.upsert_budgets(db, trip_id, budget_upsert)
    
    return {"budgets": created_budgets}

@router.get("/{trip_id}")
def get_trip_budget(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 권한 확인
    trip_member = trip_crud.get_trip_member(db, trip_id, current_user.id)
    if not trip_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this trip")
        
    budgets = budget_crud.get_budgets_by_trip(db, trip_id)
    return {"budgets": budgets}

@router.get("/{trip_id}/summary")
def get_budget_summary(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 권한 확인
    trip_member = trip_crud.get_trip_member(db, trip_id, current_user.id)
    if not trip_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this trip")
        
    summary = budget_service.get_budget_summary(db, trip_id, current_user.id)
    if not summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
        
    return summary
