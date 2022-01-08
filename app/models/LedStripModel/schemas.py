from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class LedStripBase(BaseModel):
    state: bool
    color_red: int
    color_green: int
    color_blue: int

class LedStripCreate(LedStripBase):
    pass

class LedStrip(LedStripBase):
    id: int
    device_id: int
    owner_id: int
    createdDate: datetime

    class Config:
        orm_mode = True
