from datetime import datetime, timedelta
from typing import Optional, List

import json
import httpx
from models.UserModel import crud, schemas
from models.DeviceModel import crud as deviceCrud
from database import SessionLocal
from sqlalchemy.orm import Session

from fastapi import Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from jose import JWTError, jwt
from passlib.context import CryptContext

from random import randint

config_file = open("config.json", "r")
config_file_data = json.load(config_file)

SECRET_KEY = config_file_data["jwt_config"]["SECRET_KEY"]
ALGORITHM = config_file_data["jwt_config"]["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = config_file_data["jwt_config"]["ACCESS_TOKEN_EXPIRE_MINUTES"]

#config_file.close()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login/AuthorizeButton")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None

class BaseDevice(BaseModel):
    name: str
    type: str
    ip_address: str
    get_endpoint: str
    post_endpoint: str

class Device(BaseDevice):
    deviceID: str

    
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
            status_code=403, detail="Username already registered")

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
    userToReturn = schemas.User(id = user.id, username = user.username, email = user.email)
    return userToReturn


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
    userToReturn = schemas.User(id = user.id, username = user.username, email = user.email)
    return userToReturn


async def get_current_user_id(current_user: schemas.User = Depends(get_current_user)):
    return current_user.id

async def is_current_user_an_admin(current_user: schemas.User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Insufficent permissions")
    return current_user

def get_request_ip(request: Request):
    print(request.client.host)
    return request.client.host

def is_ip_in_config(request: Request, db:Session):

    devices_ips_from_db = deviceCrud.get_all_devices_ips(db)
    device_ips = []
    for device in devices_ips_from_db:
        device_ips.append(device.ip_address)

    '''
    To bedzie dzialac tylko i wylacznie w sieci lokalnej wiec tymczasowowo nie bedzie sprawdzalo adresow
    '''

    # ## LOCAL ###
    # ipToReturn = request.client.host
    # if ipToReturn in device_ips:
    #     return True
    # raise HTTPException(status_code=403, detail="device is not registered") 
    
    # ----- OLD -----
    # ipToReturn = request.client.host
    # for element in config_file_data:
    #     if(ipToReturn == config_file_data[element]["ip_address"]):
    #         return True
    # raise HTTPException(status_code=403, detail="device is not registered")
    # ---------------
    
    return True


def is_device_in_config(deviceId, userId, type, db: Session):
    db_obj = deviceCrud.is_device_available_for_user(db, userId, deviceId)
    if not db_obj:
        return device_error()

    if db_obj.type != type:
        return device_type_error()
    
    return True

def get_id_from_ip(device_ip, type, db: Session):
    db_obj = deviceCrud.get_device_by_ip_for_device(db, device_ip)
    if not db_obj:
        return device_error()
    if db_obj.type != type:
        return device_type_error()
    return db_obj.id
    

def get_ip_from_id(deviceId, userId, type, db: Session):
    db_obj = deviceCrud.is_device_available_for_user(db, userId, deviceId)
    if not db_obj:
        return device_error()
    if db_obj.type != type:
        return device_type_error()
    return db_obj.ip_address

def get_post_endpoint_from_id(deviceId, userId, type, db: Session):
    db_obj = deviceCrud.is_device_available_for_user(db, userId, deviceId)
    if not db_obj:
        return device_error()
    if db_obj.type != type:
        return device_type_error()
    return db_obj.post_endpoint

def get_get_endpoint_from_id(deviceId, userId, type, db: Session):
    db_obj = deviceCrud.is_device_available_for_user(db, userId, deviceId)
    if not db_obj:
        return device_error()
    if db_obj.type != type:
        return device_type_error()
    return db_obj.post_endpoint


def send_data_to_esp(url, data):
    try:
        response = httpx.post(url, json=data)
        return response.status_code
    except:
        return 500

def get_data_from_esp(url):
    try:
        response = httpx.get(url)
        return response
    except:
        return 500

def device_error():
    raise HTTPException(status_code=403, detail= "Device is not registered or device id is used for a different device type")

def device_type_error():
    raise HTTPException(status_code=403, detail= "Wrong device type")

def already_registered_device_error():
    raise HTTPException(status_code=403, detail= "Device is already registered")

def password_error():
   raise HTTPException(status_code=403, detail="Password did not match the requirements")

def email_error():
    raise HTTPException(status_code=403, detail="Email did not match the requirements")

def esp_error(code):
    if(code == 500):
        raise HTTPException(status_code=code, detail= "There was an error with device")
    else:
        raise HTTPException(status_code=code.status, detail= "There was an error with device")
