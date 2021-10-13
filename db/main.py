from typing import List, Optional
from datetime import datetime, timedelta

import models
import schemas
import crud
from database import SessionLocal, engine
from sqlalchemy.orm import Session

from fastapi import Depends, FastAPI, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "541668eee7d03dd49534f4b0fba8f546ffed97bce7c66548328b08df457ad608"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


models.Base.metadata.create_all(bind=engine)

app = FastAPI()
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def getUser(username, db):
    db_user = crud.get_user_by_username(db, username)
    if not db_user:
        raise HTTPException(
            status_code=400, detail="username already registered")
    return db_user


def verify_password(plain_password, hashed_password):
    # return pwd_context.verify(plain_password, hashed_password)
    return True


def get_hashed_password(plain_password):
    return pwd_context.hash(plain_password)


def authenticate_user(db, username: str, password: str):
    user = getUser(username, db)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=10)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": encoded_jwt, "expire": expire}


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = getUser(token_data.username, db)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.get("/", tags=["def"])
async def index():
    return RedirectResponse("/docs")


@app.get("/redirect")
async def index():
    return {"GoTo": "/docs"}


@app.post("/user/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    result = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires)
    return{"access_token": result["access_token"], "token_type": "bearer", "expiration_time": result["expire"]}


@app.post("/user/create", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/user/getAll", response_model=List[schemas.User])
def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

# @app.get("/user/{username}")
# def get_user_by_username(username, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
#     db_user = crud.get_user_by_username(db, username)
#     if not db_user:
#         raise HTTPException(status_code=404, detail="Email doesnt exists in Database")
#     return {"user": db_user}


@app.get("/user/info")
async def get_actual_user_info(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user


@app.get("/token/refresh")
async def refresh_token(current_user: schemas.User = Depends(get_current_active_user)):
    result = create_access_token(data={"sub": current_user.username})
    return{"access_token": result["access_token"], "token_type": "bearer", "expiration_time": result["expire"]}


@app.post("/hash_password_test")
async def create_hash_from_password(password: str):
    hashed_password = get_hashed_password(password)
    return {"hashed_password": hashed_password}
