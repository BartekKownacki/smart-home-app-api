from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas
import dependencies 
from fastapi import HTTPException
import httpx

DEVICE_TYPE = 'AC_SOCKET'

def get_last_ac_state(db: Session, deviceId: int):
    if(not dependencies.is_device_in_config(deviceId, DEVICE_TYPE)):
        return dependencies.device_error()
    
    db_obj = db.query(models.AcSocket).filter(models.AcSocket.device_id == deviceId).order_by(models.AcSocket.id.desc()).first()
    state_to_return = schemas.AcSocketBase(device_id = db_obj.device_id,
                                            state = db_obj.state,)
    return state_to_return

def create_ac_state(db: Session, acState: schemas.AcSocketCreate, user_id: int):
    createdDate = datetime.now()

    if(not dependencies.is_device_in_config(acState.device_id, DEVICE_TYPE)):
        return dependencies.device_error()

    db_acState = models.AcSocket(state= acState.state, 
                                device_id= acState.device_id,
                                # timeStampToTurnOn = acState.timeStampToTurnOn,
                                # timeStampToTurnOff = acState.timeStampToTurnOff,
                                createdDate=createdDate,
                                owner_id=user_id)
    db.add(db_acState)
    db.commit()
    db.refresh(db_acState)

    '''
        Connect to esp and send POST to change value

    '''
    ip_address = dependencies.get_ip_from_id(acState.device_id, DEVICE_TYPE)
    post_endpoint = dependencies.get_endpoint_from_id(acState.device_id, DEVICE_TYPE, "post")
    url =  ip_address + post_endpoint
    data = acState
    response = dependencies.send_data_to_esp(url, data)
    if(response.status > 400):
        return dependencies.esp_error(response)
    
    return db_acState






