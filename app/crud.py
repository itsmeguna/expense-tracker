# crud.py
from fastapi import APIRouter, Depends, HTTPException, status,Query
from app.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import extract
from sqlalchemy import func
from . import models
from datetime import datetime,date,timedelta
from .models import Expense
from .models import User
from app import models, schemas

def get_monthly_expenses(db: Session):
    now = datetime.now()
    return db.query(Expense).filter(
        extract('month', Expense.timestamp) == now.month,
        extract('year', Expense.timestamp) == now.year
    ).all()


def get_expenses_by_date_range(db: Session, start_date: datetime, end_date: datetime,user_id: int):
    # Add 1 day and subtract a microsecond to include the full end_date
    end_date = end_date + timedelta(days=1) - timedelta(microseconds=1)

    expenses = (
        db.query(models.Expense)
        .filter(models.Expense.timestamp >= start_date, models.Expense.timestamp <= end_date)
        .order_by(models.Expense.timestamp)
        .all()
    )

    total_amount = sum([e.amount for e in expenses])

    if not expenses:
        return schemas.ExpenseSummary(
            total_amount=0.0,
            expenses=[],
            message="No expenses found for the given date range."
        )

    return schemas.ExpenseSummary(
        total_amount=total_amount,
        expenses=expenses
    )

def get_expenses_grouped_by_category(db: Session):
    return (
        db.query(models.Expense.category, func.sum(models.Expense.amount).label("total_amount"))
        .group_by(models.Expense.category)
        .all()
    )
