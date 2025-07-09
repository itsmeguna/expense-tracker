from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from app.database import get_db
from app import models
from app.schemas import MonthlySummary
from datetime import date
import calendar
import logging
from app.auth_utils import get_current_user
from app.models import User

router = APIRouter(prefix="/summary", tags=["Summary"])

logger = logging.getLogger(__name__)

@router.get("/monthly")
def get_monthly_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logger.info(f"User {current_user.id} requested monthly summary")

    # Get unique months from all tables for the current user
    months_income = db.query(
        extract('year', models.Income.timestamp).label("year"),
        extract('month', models.Income.timestamp).label("month")
    ).filter(models.Income.user_id == current_user.id).distinct()

    months_expense = db.query(
        extract('year', models.Expense.timestamp).label("year"),
        extract('month', models.Expense.timestamp).label("month")
    ).filter(models.Expense.user_id == current_user.id).distinct()

    months_saving = db.query(
        extract('year', models.Saving.timestamp).label("year"),
        extract('month', models.Saving.timestamp).label("month")
    ).filter(models.Saving.user_id == current_user.id).distinct()

    all_months_set = {
        (int(m.year), int(m.month)) for m in
        list(months_income) + list(months_expense) + list(months_saving)
    }

    results = []

    for year, month in sorted(all_months_set, reverse=True):
        month_label = f"{year}-{str(month).zfill(2)}"
        logger.info(f"Processing summary for {month_label} for user {current_user.id}")

        income = db.query(func.sum(models.Income.amount)).filter(
            extract('year', models.Income.timestamp) == year,
            extract('month', models.Income.timestamp) == month,
            models.Income.user_id == current_user.id
        ).scalar()

        expense = db.query(func.sum(models.Expense.amount)).filter(
            extract('year', models.Expense.timestamp) == year,
            extract('month', models.Expense.timestamp) == month,
            models.Expense.user_id == current_user.id
        ).scalar()

        saving = db.query(func.sum(models.Saving.amount)).filter(
            extract('year', models.Saving.timestamp) == year,
            extract('month', models.Saving.timestamp) == month,
            models.Saving.user_id == current_user.id
        ).scalar()

        income_val = round(income, 2) if income else "-"
        expense_val = round(expense, 2) if expense else "-"
        saving_val = round(saving, 2) if saving else "-"

        if all(isinstance(v, (int, float)) for v in [income_val, expense_val, saving_val]):
            balance = round(income_val - expense_val - saving_val, 2)
        else:
            balance = "-"

        results.append({
            "month": month_label,
            "total_income": income_val,
            "total_expense": expense_val,
            "total_saving": saving_val,
            "balance": balance
        })

    return results


@router.get("/monthly/{month}", response_model=MonthlySummary)
def get_summary_for_month(
    month: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Example month format: "2025-06"
    """
    logger.info(f"User {current_user.id} requested summary for month: {month}")

    year, month_num = map(int, month.split("-"))
    start_date = date(year, month_num, 1)
    last_day = calendar.monthrange(year, month_num)[1]
    end_date = date(year, month_num, last_day)

    income = db.query(func.sum(models.Income.amount)).filter(
        models.Income.timestamp.between(start_date, end_date),
        models.Income.user_id == current_user.id
    ).scalar()

    expense = db.query(func.sum(models.Expense.amount)).filter(
        models.Expense.timestamp.between(start_date, end_date),
        models.Expense.user_id == current_user.id
    ).scalar()

    saving = db.query(func.sum(models.Saving.amount)).filter(
        models.Saving.timestamp.between(start_date, end_date),
        models.Saving.user_id == current_user.id
    ).scalar()

    return {
        "month": month,
        "total_income": income or "0.0",
        "total_expense": expense or "0.0",
        "total_saving": saving or "0.0",
        "balance": (income or 0) - (expense or 0) - (saving or 0) if income or expense or saving else "-"
    }
