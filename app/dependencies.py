from datetime import datetime, timedelta
from typing import Optional, List

import json

from models.UserModel import crud, schemas
from database import SessionLocal
from sqlalchemy.orm import Session

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from jose import JWTError, jwt
from passlib.context import CryptContext

config_file = open("config.json", "r")
config_file_data = json.load(config_file)

SECRET_KEY = config_file_data["jwt_config"]["SECRET_KEY"]
ALGORITHM = config_file_data["jwt_config"]["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = config_file_data["jwt_config"]["ACCESS_TOKEN_EXPIRE_MINUTES"]

#config_file.close()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None

class Device(BaseModel):
    name: str
    type: str
    deviceID: int
    ip_address: str
    get_endpoint: List[str]
    post_endpoint: List[str]

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
    return pwd_context.verify(plain_password, hashed_password)


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

async def get_current_active_user_id(current_user: schemas.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user.id

def get_devices_config():
    config_file = open("config_devices.json", "r")
    DEVICES = json.load(config_file)
    return DEVICES

def add_device_to_config(device: Device):
    with open("config_devices.json",'r+') as file:
        file_data = json.load(file)
        devices_json_object = {
            device.name: {
                "name": device.name,
                "type": device.type,
                "deviceID": device.deviceID,
                "ip_address": device.ip_address,
                "endpoints": {
                    "get": device.get_endpoint,
                    "post": device.post_endpoint
                }
            }
        }

        file_data.update(devices_json_object)
        file.seek(0)
        json.dump(file_data, file, indent = 4)
        print(file)
    return device.name

def remove_device_from_config(device_name: str):    
    with open("config_devices.json",'r+') as file:
        file_data = json.load(file)
        for element in file_data:
            if element == device_name:
                file_data.pop(element)
                break
        print(file_data)

    with open('config_devices.json', 'w') as dest_file:
        dest_file.write(json.dumps(file_data))
    return True

