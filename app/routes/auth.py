from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app import models, database,auth_utils
from app import models, schemas 
from app.database import get_db
import logging
from datetime import timedelta
from app.auth_utils import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.auth_utils import get_current_user_from_bearer




router = APIRouter(tags=["Authentication"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = auth_utils.hash_password(user.password)
    new_user = models.User(username=user.username, email=user.email, password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # ✅ LOG the registration (no password!)
    logger.info(f"New user registered: username={new_user.username}, email={new_user.email}")

    return new_user

@router.post("/login")
def login_user(login_data: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == login_data.email).first()

    if not user or not auth_utils.verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    #access_token = auth_utils.create_access_token(data={"user_id": user.id})
   

   # Example user object with .id
    access_token = create_access_token(
    data={"user_id": user.id},
    expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )


    logger.info(f"User logged in successfully: username={user.username}, id={user.id}")

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token")
def login_for_swagger(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    if not user or not auth_utils.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"user_id": user.id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/protected")
def protected_route(current_user: models.User = Depends(auth_utils.get_current_user)):
    return {"message": f"Hello, {current_user.username}!"}
