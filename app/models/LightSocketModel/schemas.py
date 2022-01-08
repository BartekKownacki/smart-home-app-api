from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import json

class LightSocketBase(BaseModel):
    state: str
    
    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
            
class LightSocketCreate(LightSocketBase):
    state: bool
    
class LightSocket(LightSocketBase):
    id: int
    device_id: int
    owner_id: int
    createdDate: datetime

    class Config:
        orm_mode = True
