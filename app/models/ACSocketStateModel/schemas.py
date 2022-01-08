from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class AcSocketBase(BaseModel):
    state: bool

class AcSocketCreate(AcSocketBase):
    pass

class AcSocket(AcSocketBase):
    device_id: int
    id: int
    owner_id: int
    createdDate: datetime

    class Config:
        orm_mode = True
