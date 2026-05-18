from sqlalchemy.orm import Session
from datetime import datetime
from app.crud import budget as budget_crud
from app.crud import trip as trip_crud
from app.schemas.budget import BudgetUpsert
from app.services.exchange_service import get_exchange_rate

def upsert_budgets(db: Session, trip_id: int, budget_upsert: BudgetUpsert):
    # 기존 budget 삭제
    existing_budgets = budget_crud.get_budgets_by_trip(db, trip_id)
    for b in existing_budgets:
        budget_crud.delete_budget(db, b.id)
    
    # 환율 조회용 오늘 날짜
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    created_budgets = []
    for b_in in budget_upsert.budgets:
        # amount_krw 계산
        if not b_in.amount_krw:
            rate, _ = get_exchange_rate(today_str, b_in.currency, "KRW")
            b_in.amount_krw = float(b_in.amount) * rate
            
        new_budget = budget_crud.create_budget(db, trip_id, b_in)
        # SQLAlchemy 객체가 루프 안의 commit() 때문에 만료(expired)되어 빈 객체로 반환되는 것을 막기 위해 dict로 변환
        created_budgets.append({c.name: getattr(new_budget, c.name) for c in new_budget.__table__.columns})
        
    return created_budgets

def get_budget_summary(db: Session, trip_id: int, user_id: int):
    trip = trip_crud.get_trip_by_id(db, trip_id)
    if not trip:
        return None
        
    budgets = budget_crud.get_budgets_by_trip(db, trip_id)
    total_budget_krw = sum([float(b.amount_krw or b.amount or 0) for b in budgets])
    
    expenses = budget_crud.get_expenses_by_trip(db, trip_id)
    
    # shared + 본인 personal expense 합산
    filtered_expenses = [
        e for e in expenses 
        if e.expense_type == "shared" or (e.expense_type == "personal" and e.created_by == user_id)
    ]
    total_expense_krw = sum([float(e.amount_krw or e.amount_original or 0) for e in filtered_expenses])
    
    # 여행 진행률 계산
    today = datetime.now().date()
    start_date = trip.start_date
    end_date = trip.end_date
    
    if start_date and end_date and end_date >= start_date:
        total_days = (end_date - start_date).days + 1
        days_passed = (today - start_date).days + 1
        if days_passed < 1:
            days_passed = 0
        elif days_passed > total_days:
            days_passed = total_days
        progress_rate = days_passed / total_days
    else:
        progress_rate = 1.0

    # 소비율
    if total_budget_krw > 0:
        consumption_rate = total_expense_krw / total_budget_krw
    else:
        consumption_rate = 0.0

    # burn_rate 계산
    if progress_rate > 0:
        burn_rate = consumption_rate / progress_rate
    else:
        # 여행 첫날(진행률 = 0) 또는 시작 전 -> 소비율만으로 판단
        burn_rate = consumption_rate

    # risk_status 판별
    if burn_rate < 1.0:
        risk_status = "safe"
    elif 1.0 <= burn_rate < 1.3:
        risk_status = "warning"
    else:
        risk_status = "danger"
        
    # category_stats 계산
    category_stats = {}
    for b in budgets:
        cat = b.category
        val = float(b.amount_krw or b.amount or 0)
        if cat not in category_stats:
            category_stats[cat] = {"budget": val, "expense": 0.0}
        else:
            category_stats[cat]["budget"] += val
            
    for e in filtered_expenses:
        cat = e.category or "uncategorized"
        val = float(e.amount_krw or e.amount_original or 0)
        if cat not in category_stats:
            category_stats[cat] = {"budget": 0.0, "expense": val}
        else:
            category_stats[cat]["expense"] += val

    return {
        "total_budget_krw": total_budget_krw,
        "total_expense_krw": total_expense_krw,
        "burn_rate": round(burn_rate, 2),
        "risk_status": risk_status,
        "category_stats": category_stats
    }
