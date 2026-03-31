from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import date, timedelta
from typing import List, Optional
from . import models, schemas

# CREATE
def create_expense(db: Session, expense: schemas.ExpenseCreate) -> models.Expense:
    db_expense = models.Expense(
        description=expense.description,
        amount=expense.amount,
        date=expense.date,
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def bulk_create_expenses(
    db: Session, expenses: List[schemas.ExpenseCreate]
) -> List[models.Expense]:
    db_expenses = [
        models.Expense(description=e.description, amount=e.amount, date=e.date)
        for e in expenses
    ]
    db.add_all(db_expenses)
    db.commit()
    for exp in db_expenses:
        db.refresh(exp)
    return db_expenses

# READ
def get_expense(db: Session, expense_id: int) -> Optional[models.Expense]:
    return db.query(models.Expense).filter(models.Expense.id == expense_id).first()

def get_expenses(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.Expense]:
    return db.query(models.Expense).order_by(models.Expense.date.desc()).offset(skip).limit(limit).all()

# UPDATE
def update_expense(
    db: Session, expense_id: int, updates: schemas.ExpenseUpdate
) -> Optional[models.Expense]:
    db_expense = get_expense(db, expense_id)
    if not db_expense:
        return None
    patch_data = updates.model_dump(exclude_unset=True)
    for field, value in patch_data.items():
        setattr(db_expense, field, value)
    db.commit()
    db.refresh(db_expense)
    return db_expense

# DELETE
def delete_expense(db: Session, expense_id: int) -> bool:
    db_expense = get_expense(db, expense_id)
    if not db_expense:
        return False
    db.delete(db_expense)
    db.commit()
    return True

# REPORTS
def summary_by_shop(db: Session) -> List[dict]:
    results = (
        db.query(
            models.Expense.description,
            func.sum(models.Expense.amount).label("total"),
        )
        .group_by(models.Expense.description)
        .order_by(func.sum(models.Expense.amount).desc())
        .all()
    )
    return [{"shop": r.description, "total": float(r.total)} for r in results]

def weekly_total(db: Session) -> float:
    since = date.today() - timedelta(days=7)
    total = (
        db.query(func.sum(models.Expense.amount))
        .filter(models.Expense.date >= since)
        .scalar()
    )
    return float(total or 0)

def monthly_total(db: Session, month: int, year: int) -> float:
    total = (
        db.query(func.sum(models.Expense.amount))
        .filter(
            extract("month", models.Expense.date) == month,
            extract("year",  models.Expense.date) == year,
        )
        .scalar()
    )
    return float(total or 0)

def yearly_total(db: Session, year: int) -> float:
    total = (
        db.query(func.sum(models.Expense.amount))
        .filter(extract("year", models.Expense.date) == year)
        .scalar()
    )
    return float(total or 0)
