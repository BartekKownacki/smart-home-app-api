from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas
import dependencies 
from fastapi import HTTPException
import httpx


'''
Create device
get devices list
'''

def get_all_devices_ips(db: Session):
    db_obj = db.query(models.Device).all()
    return db_obj

def is_device_available_for_user(db: Session, userId=int, deviceId = str):
    db_obj = db.query(models.Device).filter(models.Device.owner_id == userId).filter(models.Device.id == deviceId).first()
    return db_obj

def get_device_by_ip_for_device(db: Session, deviceIp = str):
    db_obj = db.query(models.Device).filter(models.Device.ip_address == deviceIp).first()
    return db_obj

def get_device_by_ip(db: Session, userId=int, deviceIp = str):
    db_obj = db.query(models.Device).filter(models.Device.owner_id == userId).filter(models.Device.ip_address == deviceIp).all()
    return db_obj

def get_devices_for_user_id(db: Session, userId: int):    
    db_obj = db.query(models.Device).filter(models.Device.owner_id == userId).all()
    if len(db_obj) == 0:
        return dependencies.device_error()
    
    state_to_return = []
    for device in db_obj:
        state_to_return.append(schemas.DeviceReturn(name = device.name,
                                            deviceID = device.id,
                                            type = device.type,
                                            ip_address = device.ip_address)) 
    return state_to_return

def create_new_device(db: Session, device: schemas.DeviceCreate, user_id: int):
    db_newDevice = models.Device(name= device.name, 
                                type= device.type,
                                ip_address=device.ip_address,
                                post_endpoint=device.post_endpoint,
                                get_endpoint=device.get_endpoint,
                                owner_id=user_id)
    db.add(db_newDevice)
    db.commit()
    db.refresh(db_newDevice)
    return db_newDevice.id

def delete_device_by_id(db: Session, deviceId: int, userId):
    db_obj = db.query(models.Device).filter(models.Device.owner_id == userId).filter(models.Device.id == deviceId).first()
    if not db_obj:
        return dependencies.device_error()

    db.delete(db_obj)
    db.commit()
    return True






