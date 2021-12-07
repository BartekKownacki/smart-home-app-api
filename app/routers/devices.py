from typing import List
from pydantic import BaseModel
import dependencies
from database import SessionLocal, engine

from fastapi import Depends, APIRouter

import json

router = APIRouter(
    prefix="/devices",
    tags=["Devices config actions"],
    responses={404: {"description": "Not found"}},
)

class Device(BaseModel):
    name: str
    type: str
    deviceID: int
    ip_address: str
    endpoints: dict[str, str]



@router.get("/getconfig", response_model=List[Device])
async def get_devices_config(current_user_id: int = Depends(dependencies.get_current_user_id)):
    return dependencies.get_devices_config()

@router.post("/addnew", response_model= int)
async def add_new_device(device: dependencies.BaseDevice, current_user_id: int = Depends(dependencies.get_current_user_id)):
    new_device_name = dependencies.add_device_to_config(device)
    return new_device_name

@router.delete("/delete/{device_id}", response_model=bool)
async def delete_device_by_device_id(device_id: int, current_user_id: int = Depends(dependencies.get_current_user_id)):
    success = dependencies.remove_device_from_config(device_id)
    return success
