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



@router.get("/getconfig")
async def get_devices_config(current_user_id: int = Depends(dependencies.get_current_active_user_id)):
    return dependencies.get_devices_config()

@router.post("/addnew")
async def add_new_device(device: dependencies.Device, current_user_id: int = Depends(dependencies.get_current_active_user_id)):
    new_device_name = dependencies.add_device_to_config(device)
    return new_device_name

@router.delete("/delete/{device_name}")
async def delete_device_by_device_name(device_name: str, current_user_id: int = Depends(dependencies.get_current_active_user_id)):
    success = dependencies.remove_device_from_config(device_name)
    return success
