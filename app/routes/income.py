from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from app.models import Income, User
from app.schemas import IncomeCreate, IncomeResponse
from app.database import get_db
from app.auth_utils import get_current_user

router = APIRouter(prefix="/income", tags=["Income"])
logger = logging.getLogger(__name__)

@router.post("/", response_model=IncomeResponse)
def create_income(
    income: IncomeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_income = Income(**income.dict(), user_id=current_user.id)
    db.add(new_income)
    db.commit()
    db.refresh(new_income)

    logger.info(f"User {current_user.id} created income: {new_income.amount} at {new_income.timestamp}")
    return new_income


@router.get("/", response_model=list[IncomeResponse])
def get_all_income(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    incomes = db.query(Income).filter(Income.user_id == current_user.id).order_by(Income.timestamp.desc()).all()
    logger.info(f"User {current_user.id} fetched {len(incomes)} income records")
    return incomes
