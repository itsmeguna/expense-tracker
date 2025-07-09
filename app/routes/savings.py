from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from app import models, schemas
from app.database import get_db
from app.auth_utils import get_current_user
from app.models import User

router = APIRouter(prefix="/saving", tags=["Saving"])
logger = logging.getLogger(__name__)

@router.post("/", response_model=schemas.Saving)
def create_saving(
    saving: schemas.SavingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_saving = models.Saving(**saving.dict(), user_id=current_user.id)
    db.add(new_saving)
    db.commit()
    db.refresh(new_saving)

    logger.info(f"User {current_user.id} created saving: {new_saving.amount} at {new_saving.timestamp}")
    return new_saving


@router.get("/", response_model=List[schemas.Saving])
def get_all_saving(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    savings = db.query(models.Saving).filter(models.Saving.user_id == current_user.id).order_by(models.Saving.timestamp.desc()).all()
    logger.info(f"User {current_user.id} retrieved {len(savings)} saving records")
    return savings
