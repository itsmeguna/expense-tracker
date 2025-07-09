from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, crud, auth_utils
from app.database import get_db
from datetime import datetime
from sqlalchemy import func
from app.models import Expense
import logging

router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"]
)

logger = logging.getLogger(__name__)


# ✅ GET all expenses (for current user)
@router.get("/", response_model=List[schemas.Expenseout])
def get_expenses(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    logger.info(f"User {current_user.id} requested all expenses")
    return db.query(Expense).filter(Expense.user_id == current_user.id).all()


# ✅ POST new expense
@router.post("/", response_model=schemas.Expenseout)
def create_expense(
    expense: schemas.ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    new_expense = Expense(
        amount=expense.amount,
        category=expense.category,
        Note=expense.Note,
        user_id=current_user.id
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    logger.info(f"Expense created by user {current_user.id}: {new_expense}")
    return new_expense


# ✅ GET monthly grouped expenses
"""@router.get("/month", response_model=List[schemas.Expenseout])
def monthly_expenses(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    logger.info(f"User {current_user.id} requested monthly expenses")
    return crud.get_monthly_expenses(db, user_id=current_user.id)"""


# ✅ GET expenses summary (GET with query params)
@router.get("/by_date", response_model=schemas.ExpenseSummary)
def get_expenses_by_date_range(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="Invalid date range: start_date cannot be after end_date"
        )
    logger.info(f"User {current_user.id} requested summary from {start_date} to {end_date}")
    return crud.get_expenses_by_date_range(db, start_date, end_date, user_id=current_user.id)


# ✅ POST summary with date range in body
@router.post("/by_date", response_model=schemas.ExpenseSummary)
def get_expenses_by_date_range_post(
    date_range: schemas.DateRange,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    if date_range.start_date > date_range.end_date:
        raise HTTPException(
            status_code=400,
            detail="Invalid date range: start_date cannot be after end_date"
        )
    logger.info(f"User {current_user.id} posted date summary: {date_range}")
    return crud.get_expenses_by_date_range(db, date_range.start_date, date_range.end_date, user_id=current_user.id)


# ✅ Category summary
@router.get("/all_category", response_model=schemas.CategorySummaryResponse)
def get_category_summary(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    logger.info(f"User {current_user.id} requested category summary")
    summary = (
        db.query(Expense.category, func.sum(Expense.amount).label("total_amount"))
        .filter(
            Expense.user_id == current_user.id,
            Expense.timestamp >= start_date,
            Expense.timestamp <= end_date
        )
        .group_by(Expense.category)
        .all()
    )
    categories = [{"category": row.category, "total_amount": row.total_amount} for row in summary]
    total = sum(row["total_amount"] for row in categories)
    return {"total_amount": total, "categories": categories}


# ✅ Expenses by category
@router.post("/by-category", response_model=schemas.ExpensesByCategoryResponse)
def get_expenses_by_category(
    payload: schemas.ExpensesByCategoryRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    expenses = db.query(Expense).filter(
        Expense.user_id == current_user.id,
        Expense.category == payload.category,
        Expense.timestamp >= payload.start_date,
        Expense.timestamp <= payload.end_date
    ).all()

    total = sum(e.amount for e in expenses)

    return {
        "total_amount": total,
        "expenses": expenses
    }


# ✅ GET expense by ID
@router.get("/{id}", response_model=schemas.Expenseout)
def get_expense(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    expense = db.query(Expense).filter(Expense.id == id, Expense.user_id == current_user.id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


# ✅ DELETE expense
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    expense = db.query(Expense).filter(Expense.id == id, Expense.user_id == current_user.id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(expense)
    db.commit()
    logger.info(f"User {current_user.id} deleted expense {id}")
    return


# ✅ UPDATE expense
@router.put("/{id}", response_model=schemas.Expenseout)
def update_expense(
    id: int,
    updated_expense: schemas.ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    expense_query = db.query(Expense).filter(Expense.id == id, Expense.user_id == current_user.id)
    existing_expense = expense_query.first()
    if not existing_expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    expense_query.update(updated_expense.dict(), synchronize_session=False)
    db.commit()
    updated = expense_query.first()
    logger.info(f"User {current_user.id} updated expense {id}")
    return updated
