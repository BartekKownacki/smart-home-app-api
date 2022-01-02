from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class AcSocketBase(BaseModel):
    device_id: int
    state: bool
    # timeStampToTurnOn: Optional[datetime] = None
    # timeStampToTurnOff: Optional[datetime] = None
    

class AcSocketCreate(AcSocketBase):
    pass

class AcSocket(AcSocketBase):
    id: int
    owner_id: int
    createdDate: datetime

    class Config:
        orm_mode = True
