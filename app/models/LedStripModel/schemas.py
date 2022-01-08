from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

import json

class LedStripBase(BaseModel):
    state: str
    color_red: int
    color_green: int
    color_blue: int
    
    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

class LedStripCreate(LedStripBase):
    state: bool

class LedStrip(LedStripBase):
    id: int
    device_id: int
    owner_id: int
    createdDate: datetime

    class Config:
        orm_mode = True
