from typing import List, Optional
from datetime import datetime, timedelta

from models.UserModel import crud, schemas
import dependencies
from database import SessionLocal, engine
from sqlalchemy.orm import Session

from fastapi import Depends, FastAPI, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse

from pydantic import BaseModel
router = APIRouter(
    prefix="/user",
    tags=["Account actions"],
    responses={404: {"description": "Not found"}},
)

@router.post("/login", response_model=schemas.LoginResponse)
async def login(form_data: schemas.LoginSchema , db: Session = Depends(dependencies.get_db)):
    user = dependencies.authenticate_user(
        db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=dependencies.ACCESS_TOKEN_EXPIRE_MINUTES)
    result = dependencies.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires)
    return{"access_token": result["access_token"], "token_type": "bearer", "expiration_time": result["expire"]}

@router.post("/login/AuthorizeButton", response_model=schemas.LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends() , db: Session = Depends(dependencies.get_db)):
    user = dependencies.authenticate_user(
        db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=dependencies.ACCESS_TOKEN_EXPIRE_MINUTES)
    result = dependencies.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires)
    return{"access_token": result["access_token"], "token_type": "bearer", "expiration_time": result["expire"]}

@router.post("/create", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(dependencies.get_db)):
    db_user = crud.get_user_by_username_email(db, username=user.username, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Uername or email already registered")
    return crud.create_user(db=db, user=user)


@router.get("/getAll", response_model=List[schemas.User])
def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(dependencies.get_db), current_user: schemas.User = Depends(dependencies.get_current_user)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/info",  response_model=schemas.User)
async def get_actual_user_info(current_user: schemas.User = Depends(dependencies.get_current_user)):
    return current_user


@router.get("/token/refresh")
async def refresh_token(current_user: schemas.User = Depends(dependencies.get_current_user)):
    result = dependencies.create_access_token(
        data={"sub": current_user.username})
    return{"access_token": result["access_token"], "token_type": "bearer", "expiration_time": result["expire"]}


@router.post("/hash_password_test")
async def create_hash_from_password(password: str):
    hashed_password = dependencies.get_hashed_password(password)
    return {"hashed_password": hashed_password}


