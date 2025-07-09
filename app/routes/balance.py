from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging

from app.database import get_db
from app.models import Income, Expense, Saving, User
from app.auth_utils import get_current_user

router = APIRouter(prefix="/balance", tags=["Balance"])

logger = logging.getLogger(__name__)

@router.get("/")
def get_balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logger.info(f"User {current_user.id} requested balance")

    total_income = db.query(func.coalesce(func.sum(Income.amount), 0.0)).filter(
        Income.user_id == current_user.id
    ).scalar()

    total_expense = db.query(func.coalesce(func.sum(Expense.amount), 0.0)).filter(
        Expense.user_id == current_user.id
    ).scalar()

    total_saving = db.query(func.coalesce(func.sum(Saving.amount), 0.0)).filter(
        Saving.user_id == current_user.id
    ).scalar()

    balance = total_income - total_expense - total_saving

    logger.info(
        f"Balance for user {current_user.id} - Income: {total_income}, "
        f"Expense: {total_expense}, Saving: {total_saving}, Balance: {balance}"
    )

    return {
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "total_saving": round(total_saving, 2),
        "balance": round(balance, 2)
    }
