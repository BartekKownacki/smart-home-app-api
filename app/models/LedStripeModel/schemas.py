from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class LedStripeBase(BaseModel):
    state: bool
    color_red: int
    color_green: int
    color_blue: int

class LedStripeCreate(LedStripeBase):
    pass


class LedStripe(LedStripeBase):
    id: int
    owner_id: int
    createdDate: datetime

    class Config:
        orm_mode = True
