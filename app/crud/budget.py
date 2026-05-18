from sqlalchemy.orm import Session
from app.models.budget import Budget, Expense, ExpenseSplit
from app.schemas.budget import BudgetCreate, ExpenseCreate
from typing import Optional, List
from datetime import datetime


# ============ Budget CRUD ============

def create_budget(db: Session, trip_id: int, budget_in: BudgetCreate) -> Budget:
    """Create a new budget"""
    db_budget = Budget(
        trip_id=trip_id,
        category=budget_in.category,
        amount=budget_in.amount,
        currency=budget_in.currency,
        amount_krw=budget_in.amount_krw
    )
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget


def get_budget_by_id(db: Session, budget_id: int) -> Optional[Budget]:
    """Get budget by ID"""
    return db.query(Budget).filter(Budget.id == budget_id).first()


def get_budgets_by_trip(db: Session, trip_id: int) -> List[Budget]:
    """Get all budgets for a trip"""
    return db.query(Budget).filter(Budget.trip_id == trip_id).all()


def update_budget(db: Session, budget_id: int, **kwargs) -> Optional[Budget]:
    """Update budget"""
    db_budget = get_budget_by_id(db, budget_id)
    if not db_budget:
        return None
    
    for key, value in kwargs.items():
        if hasattr(db_budget, key) and value is not None:
            setattr(db_budget, key, value)
    
    db.commit()
    db.refresh(db_budget)
    return db_budget


def delete_budget(db: Session, budget_id: int) -> bool:
    """Delete budget"""
    db_budget = get_budget_by_id(db, budget_id)
    if not db_budget:
        return False
    
    db.delete(db_budget)
    db.commit()
    return True


# ============ Expense CRUD ============

def create_expense(
    db: Session,
    trip_id: int,
    created_by: int,
    title: str,
    amount_original: float,
    expense_date,
    expense_type: str = "shared",
    category: Optional[str] = None,
    currency: Optional[str] = "KRW",
    amount_krw: Optional[float] = None,
    memo: Optional[str] = None,
    receipt_id: Optional[int] = None
) -> Expense:
    """Create a new expense"""
    db_expense = Expense(
        trip_id=trip_id,
        created_by=created_by,
        expense_type=expense_type,
        title=title,
        category=category,
        amount_original=amount_original,
        currency=currency,
        amount_krw=amount_krw or amount_original,
        expense_date=expense_date,
        memo=memo,
        receipt_id=receipt_id
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def get_expense_by_id(db: Session, expense_id: int) -> Optional[Expense]:
    """Get expense by ID"""
    return db.query(Expense).filter(Expense.id == expense_id).first()


def get_expenses_by_trip(db: Session, trip_id: int) -> List[Expense]:
    """Get all expenses for a trip"""
    return db.query(Expense).filter(Expense.trip_id == trip_id).all()


def get_expenses_by_user(db: Session, trip_id: int, user_id: int) -> List[Expense]:
    """Get expenses created by a specific user in a trip"""
    return db.query(Expense).filter(
        Expense.trip_id == trip_id,
        Expense.created_by == user_id
    ).all()


def update_expense(db: Session, expense_id: int, **kwargs) -> Optional[Expense]:
    """Update expense"""
    db_expense = get_expense_by_id(db, expense_id)
    if not db_expense:
        return None
    
    for key, value in kwargs.items():
        if hasattr(db_expense, key) and value is not None:
            setattr(db_expense, key, value)
    
    db.commit()
    db.refresh(db_expense)
    return db_expense


def delete_expense(db: Session, expense_id: int) -> bool:
    """Delete expense"""
    db_expense = get_expense_by_id(db, expense_id)
    if not db_expense:
        return False
    
    # Delete associated splits
    db.query(ExpenseSplit).filter(ExpenseSplit.expense_id == expense_id).delete()
    
    db.delete(db_expense)
    db.commit()
    return True


def get_expense_total_by_trip(db: Session, trip_id: int) -> float:
    """Get total expenses for a trip"""
    from sqlalchemy import func
    result = db.query(func.sum(Expense.amount_krw)).filter(
        Expense.trip_id == trip_id
    ).scalar()
    return float(result) if result else 0.0


def get_expenses_by_category(db: Session, trip_id: int) -> dict:
    """Get expenses grouped by category"""
    expenses = get_expenses_by_trip(db, trip_id)
    result = {}
    for expense in expenses:
        category = expense.category or "uncategorized"
        if category not in result:
            result[category] = {"count": 0, "total": 0}
        result[category]["count"] += 1
        result[category]["total"] += float(expense.amount_krw or 0)
    return result


# ============ ExpenseSplit CRUD ============

def create_expense_split(
    db: Session,
    expense_id: int,
    user_id: int,
    split_amount: float
) -> ExpenseSplit:
    """Create an expense split entry"""
    db_split = ExpenseSplit(
        expense_id=expense_id,
        user_id=user_id,
        split_amount=split_amount
    )
    db.add(db_split)
    db.commit()
    db.refresh(db_split)
    return db_split


def get_splits_by_expense(db: Session, expense_id: int) -> List[ExpenseSplit]:
    """Get all splits for an expense"""
    return db.query(ExpenseSplit).filter(ExpenseSplit.expense_id == expense_id).all()


def get_splits_by_user(db: Session, trip_id: int, user_id: int) -> List[ExpenseSplit]:
    """Get all splits for a user in a trip"""
    return db.query(ExpenseSplit).join(Expense).filter(
        Expense.trip_id == trip_id,
        ExpenseSplit.user_id == user_id
    ).all()


def delete_splits_by_expense(db: Session, expense_id: int) -> bool:
    """Delete all splits for an expense"""
    db.query(ExpenseSplit).filter(ExpenseSplit.expense_id == expense_id).delete()
    db.commit()
    return True
