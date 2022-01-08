from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import json

class AcSocketBase(BaseModel):
    state: str

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

class AcSocketCreate(AcSocketBase):
    state: bool

class AcSocket(AcSocketBase):
    device_id: int
    id: int
    owner_id: int
    createdDate: datetime

    class Config:
        orm_mode = True
