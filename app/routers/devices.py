from typing import List
from pydantic import BaseModel
import dependencies
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from models.DeviceModel import crud, schemas
from fastapi import Depends, APIRouter, HTTPException

import json

# Available device types: 
# TEMP_HUMID
# LED_STRIPE
# LIGHT_BULB
# AC_SOCKET

router = APIRouter(
    prefix="/devices",
    tags=["Devices config actions"],
    responses={404: {"description": "Not found"}},
)

DEVICE_TYPES = ["AC_SOCKET", "LIGHT_SWITCH", "TEMP_HUMID", "LED_STRIP"]



@router.get("/getconfig", response_model=List[schemas.DeviceReturn])
async def get_devices_config(current_user_id: int = Depends(dependencies.get_current_user_id), db: Session = Depends(dependencies.get_db)):
    return crud.get_devices_for_user_id(db, current_user_id)

@router.post("/addnew", response_model= int)
async def add_new_device(device: schemas.DeviceCreate, current_user_id: int = Depends(dependencies.get_current_user_id), db: Session = Depends(dependencies.get_db)):
    db_device = crud.get_device_by_ip(db, userId=current_user_id, deviceIp = device.ip_address)
    if len(db_device) != 0:
        raise HTTPException(status_code=400, detail="Device already registered")
    
    if not device.type in DEVICE_TYPES:
        return dependencies.device_type_error()
    
    return crud.create_new_device(db=db, device = device, user_id = current_user_id)

@router.delete("/delete/{device_id}", response_model=bool)
async def delete_device_by_device_id(device_id: int, current_user_id: int = Depends(dependencies.get_current_user_id), db: Session = Depends(dependencies.get_db)):
    success = crud.delete_device_by_id(db, device_id, current_user_id)
    return success
