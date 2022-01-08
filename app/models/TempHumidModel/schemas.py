from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

import json

class TemperatureHumidityBase(BaseModel):
    temperature: float
    humidity: float 

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

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
