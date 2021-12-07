from datetime import datetime, timedelta
from typing import Optional, List

import json

from models.UserModel import crud, schemas
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
            status_code=401, detail="username already registered")

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
    userToReturn = schemas.User(id = user.id, username = user.username, email = user.email, is_admin = user.is_admin)
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
    userToReturn = schemas.User(id = user.id, username = user.username, email = user.email, is_admin = user.is_admin)
    return userToReturn


async def get_current_user_id(current_user: schemas.User = Depends(get_current_user)):
    return current_user.id

async def is_current_user_an_admin(current_user: schemas.User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Insufficent permissions")
    return current_user

async def get_current_request_ip(request: Request):

    config_file = open("config_devices.json", "r")
    config_file_data = json.load(config_file)

    '''
    To bedzie dzialac tylko i wylacznie w sieci lokalnej wiec tymczasowowo nie bedzie sprawdzalo adresow
    '''

    # ## LOCAL ### 
    # ipToReturn = request.client.host
    # for element in config_file_data:
    #     if(ipToReturn == config_file_data[element]["ip_address"]):
    #         return True
        
    # raise HTTPException(status_code=403, detail="device not registered")

    return True


def get_devices_config():
    config_file = open("config_devices.json", "r")
    DEVICES = json.load(config_file)
    return DEVICES

def get_ids_from_config():
    with open("config_devices.json",'r+') as file:
        file_data = json.load(file)
        usedIds = [] 
        for element in file_data:
            usedIds.append(element["deviceID"])
    return usedIds

def get_ids_from_config_for_type(type):
    with open("config_devices.json",'r+') as file:
        file_data = json.load(file)
        usedIds = [] 
        for element in file_data:
            if(element["type"] == type):
                usedIds.append(element["deviceID"])
    return usedIds

def get_ips_from_config_for_type(type):
    with open("config_devices.json",'r+') as file:
        file_data = json.load(file)
        usedIps = [] 
        for element in file_data:
            if(element["type"] == type):
                usedIps.append(element["ip_address"])
    return usedIps

def is_device_in_config(deviceId, type):
    usedIds = get_ids_from_config_for_type(type)
    if(deviceId in usedIds):
        return True
    return False

def get_id_from_ip(device_ip, type):
    with open("config_devices.json",'r+') as file:
        file_data = json.load(file)
        id = 0
        for element in file_data:
            if(element["type"] == type and element["ip_address"] == device_ip):
                id = element["deviceID"]

    return id

# def is_device_in_config_by_ip(deviceIp, type):
#     usedIps = get_ips_from_config_for_type(type)
#     if(deviceIp in usedIps):
#         deviceId = 
#         return deviceIP
#     return False

def generateId(usedIds):
    if(usedIds):
        randomint = randint(10000, 99999)
        while(randomint in usedIds):
            print (randomint)
            randomint = randint(10000, 99999)
    
    return randomint

def add_device_to_config(device: Device):
    with open("config_devices.json",'r+') as file:
        file_data = json.load(file)
        
        usedIds = get_ids_from_config()

        deviceId = generateId(usedIds)

        devices_json_object = {
            "name": device.name,
            "type": device.type,
            "deviceID": deviceId,
            "ip_address": device.ip_address,
            "endpoints": {
                "get": device.get_endpoint,
                "post": device.post_endpoint
            }
        }

        file_data.append(devices_json_object)
        file.seek(0)
        json.dump(file_data, file, indent = 4)
        print(file)
    return deviceId

def remove_device_from_config(device_id: int):    
    with open("config_devices.json",'r+') as file:
        file_data = json.load(file)
        for element in file_data:
            if element["deviceID"] == device_id:
                print(element)
                file_data.remove(element)
                break
        #print(file_data)

    with open('config_devices.json', 'w') as dest_file:
        dest_file.write(json.dumps(file_data))
    return True

def device_error():
    return JSONResponse(status_code=400, content={
        "error_code": 403,
        "message": "Device is not registered or device id is used for a different device type"}, )