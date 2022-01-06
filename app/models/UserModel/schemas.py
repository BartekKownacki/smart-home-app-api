from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class LoginSchema(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expiration_time: datetime

class ChangeRoleResponse(BaseModel):
    username:str