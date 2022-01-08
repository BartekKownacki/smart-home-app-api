from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class LightSocketBase(BaseModel):
    state: bool

class LightSocketCreate(LightSocketBase):
    pass

class LightSocket(LightSocketBase):
    id: int
    device_id: int
    owner_id: int
    createdDate: datetime

    class Config:
        orm_mode = True
