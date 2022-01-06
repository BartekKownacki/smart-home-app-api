from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class TemperatureHumidityBase(BaseModel):
    temperature: float
    humidity: float 

class TemperatureHumidityCreate(TemperatureHumidityBase):
    device_ip: str

class TemperatureHumidityGet(TemperatureHumidityBase):
    device_id: int

class TemperatureHumidity(TemperatureHumidityGet):
    id: int
    owner_id: int
    createdDate: datetime

    class Config:
        orm_mode = True
