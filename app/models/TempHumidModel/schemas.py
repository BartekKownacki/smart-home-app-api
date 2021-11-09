from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class TemperatureHumidityBase(BaseModel):
    temperature: float
    humidity: float 

class TemperatureHumidityCreate(TemperatureHumidityBase):
    device_ip: str

class TemperatureHumidity(TemperatureHumidityBase):
    id: int
    device_id: int
    owner_id: int
    createdDate: datetime

    class Config:
        orm_mode = True
