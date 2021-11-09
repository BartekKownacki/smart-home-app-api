from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class LightSocketBase(BaseModel):
    device_id: int
    state: bool
    timeStampToTurnOn: Optional[datetime] = None
    timeStampToTurnOff: Optional[datetime] = None

class LightSocketCreate(LightSocketBase):
    pass


class LightSocket(LightSocketBase):
    id: int
    owner_id: int
    createdDate: datetime

    class Config:
        orm_mode = True
