from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from . import crud, models, schemas, database

# Auto-create tables on startup
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Smart Expense Tracker",
    description="An API for tracking personal expenses, with reporting.",
    version="1.0.0",
)

# EXPENSES: CRUD
@app.post(
    "/expenses",
    response_model=schemas.ExpenseOut,
    status_code=status.HTTP_201_CREATED,
    summary="Creates single expense",
    tags=["Expenses"],
)
def create_expense(
    expense: schemas.ExpenseCreate,
    db: Session = Depends(database.get_db),
):
    return crud.create_expense(db, expense)

@app.post(
    "/expenses/bulk",
    response_model=List[schemas.ExpenseOut],
    status_code=status.HTTP_201_CREATED,
    summary="Creates multiple expenses at once",
    tags=["Expenses"],
)
def bulk_create(
    expenses: List[schemas.ExpenseCreate],
    db: Session = Depends(database.get_db),
):
    if not expenses:
        raise HTTPException(status_code=400, detail="Expense list cannot be empty")
    return crud.bulk_create_expenses(db, expenses)

@app.get(
    "/expenses",
    response_model=List[schemas.ExpenseOut],
    summary="List all expenses",
    tags=["Expenses"],
)
def list_expenses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
):
    return crud.get_expenses(db, skip=skip, limit=limit)

@app.get(
    "/expenses/{expense_id}",
    response_model=schemas.ExpenseOut,
    summary="Get a single expense by ID",
    tags=["Expenses"],
)
def get_expense(expense_id: int, db: Session = Depends(database.get_db)):
    expense = crud.get_expense(db, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@app.patch(
    "/expenses/{expense_id}",
    response_model=schemas.ExpenseOut,
    summary="Partially update an expense",
    tags=["Expenses"],
)
def update_expense(
    expense_id: int,
    updates: schemas.ExpenseUpdate,
    db: Session = Depends(database.get_db),
):
    expense = crud.update_expense(db, expense_id, updates)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@app.delete(
    "/expenses/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an expense",
    tags=["Expenses"],
)
def delete_expense(expense_id: int, db: Session = Depends(database.get_db)):
    deleted = crud.delete_expense(db, expense_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Expense not found")

# REPORTS
@app.get(
    "/reports/summary",
    response_model=List[schemas.ShopSummary],
    summary="Total spending grouped by shop",
    tags=["Reports"],
)
def get_summary(db: Session = Depends(database.get_db)):
    return crud.summary_by_shop(db)

@app.get(
    "/reports/weekly",
    response_model=schemas.PeriodTotal,
    summary="Total spending in the last 7 days",
    tags=["Reports"],
)
def get_weekly(db: Session = Depends(database.get_db)):
    return {"period": "Last 7 Days", "total": crud.weekly_total(db)}

@app.get(
    "/reports/monthly",
    response_model=schemas.MonthTotal,
    summary="Total spending for a given month/year",
    tags=["Reports"],
)
def get_monthly(month: int, year: int, db: Session = Depends(database.get_db)):
    if not (1 <= month <= 12):
        raise HTTPException(status_code=400, detail="month must be 1–12")
    return {"month": month, "year": year, "total": crud.monthly_total(db, month, year)}

@app.get(
    "/reports/yearly",
    response_model=schemas.YearTotal,
    summary="Total spending for a given year",
    tags=["Reports"],
)
def get_yearly(year: int, db: Session = Depends(database.get_db)):
    return {"year": year, "total": crud.yearly_total(db, year)}
