from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class DeviceBase(BaseModel):
    name: str
    type: str
    ip_address: str
    
class DeviceReturn(DeviceBase):
    deviceID: int
    
class DeviceCreate(DeviceBase):
    get_endpoint: str
    post_endpoint: str

class Device(DeviceReturn):
    get_endpoint: str
    post_endpoint: str
    owner_id: int

    class Config:
        orm_mode = True
