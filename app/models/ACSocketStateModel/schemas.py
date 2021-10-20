from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class AcSocketBase(BaseModel):
    state: bool
    timeStampToTurnOn: Optional[datetime] = None
    timeStampToTurnOff: Optional[datetime] = None

class AcSocketCreate(AcSocketBase):
    pass


class AcSocket(AcSocketBase):
    id: int
    createdById: int
    createdDate: datetime

    class Config:
        orm_mode = True
