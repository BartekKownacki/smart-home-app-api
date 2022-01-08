from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas
import dependencies 
from fastapi import HTTPException

DEVICE_TYPE = 'AC_SOCKET'
STATE_ON = "On"
STATE_OFF = "Off"
STATE_DISCONNECTED = "Disconnected"

async def get_last_ac_state(db: Session, deviceId: int, user_id: int):
    if(not dependencies.is_device_in_config(deviceId, user_id, DEVICE_TYPE, db)):
        return dependencies.device_error()

    is_esp_online_response = await dependencies.check_is_esp_online(deviceId, user_id, DEVICE_TYPE, db)
    if is_esp_online_response.status_code > 400:
        return dependencies.esp_error(is_esp_online_response)

    db_obj = db.query(models.AcSocket).filter(models.AcSocket.device_id == deviceId).order_by(models.AcSocket.id.desc()).first()
    if not db_obj:
        return schemas.AcSocketBase(state = STATE_OFF)
    
    state_to_return = schemas.AcSocketBase(state = STATE_ON if db_obj.state else STATE_OFF)
    return state_to_return

def get_last_ac_state_for_device(db: Session, deviceIp: str):
    deviceId = dependencies.get_id_from_ip(deviceIp, DEVICE_TYPE, db)
    
    db_obj = db.query(models.AcSocket).filter(models.AcSocket.device_id == deviceId).order_by(models.AcSocket.id.desc()).first()
    if not db_obj:
        return schemas.AcSocketBase(state = STATE_OFF)

    state_to_return = schemas.AcSocketBase(device_id = db_obj.device_id,
                                            state = STATE_ON if db_obj.state else STATE_OFF)
    return state_to_return

async def create_ac_state(db: Session, acState: schemas.AcSocketCreate, user_id: int, deviceId: int):
    createdDate = datetime.now()

    if(not dependencies.is_device_in_config(deviceId, user_id, DEVICE_TYPE, db)):
        return dependencies.device_error()

    db_acState = models.AcSocket(state = acState.state, 
                                device_id= deviceId,
                                createdDate=createdDate,
                                owner_id=user_id)
    db.add(db_acState)
    db.commit()
    db.refresh(db_acState)

    '''
        Connect to esp and send POST to change value

    '''
    ip_address = dependencies.get_ip_from_id(deviceId, user_id, DEVICE_TYPE, db)
    post_endpoint = dependencies.get_post_endpoint_from_id(deviceId, user_id, DEVICE_TYPE, db)
    url =  ip_address + post_endpoint
    data = acState.toJson()
    response = await dependencies.send_data_to_esp(url, data)
    if(response.status_code > 400):
        return dependencies.esp_error(response)
    
    return db_acState