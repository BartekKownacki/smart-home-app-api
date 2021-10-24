from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class TemperatureHumidityBase(BaseModel):
    temperature: float
    humidity: float 

class TemperatureHumidityCreate(TemperatureHumidityBase):
    pass


class TemperatureHumidity(TemperatureHumidityBase):
    id: int
    owner_id: int
    createdDate: datetime

    class Config:
        orm_mode = True
