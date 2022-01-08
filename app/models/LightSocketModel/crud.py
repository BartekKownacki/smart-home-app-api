from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas
import dependencies 
from fastapi import HTTPException

DEVICE_TYPE = 'LIGHT_SWITCH'

def get_last_light_state(db: Session, deviceId: int, user_id: int):
    if(not dependencies.is_device_in_config(deviceId, user_id, DEVICE_TYPE, db)):
        return dependencies.device_error()
    
    db_obj = db.query(models.LightSocket).filter(models.LightSocket.device_id == deviceId).order_by(models.LightSocket.id.desc()).first()
    if not db_obj:
        return schemas.LightSocketBase(state = False)
    state_to_return = schemas.LightSocketBase(state = db_obj.state,)
    return state_to_return

def get_last_light_state_for_device(db: Session, deviceIp: str):
    deviceId = dependencies.get_id_from_ip(deviceIp, DEVICE_TYPE, db)
    
    db_obj = db.query(models.LightSocket).filter(models.LightSocket.device_id == deviceId).order_by(models.LightSocket.id.desc()).first()
    if not db_obj:
        return schemas.LightSocketBase(state = False)
    state_to_return = schemas.LightSocketBase(state = db_obj.state,)
    return state_to_return


def create_light_state(db: Session, lightState: schemas.LightSocketCreate, user_id: int, deviceId:int):
    createdDate = datetime.now()
    if(not dependencies.is_device_in_config(deviceId, user_id, DEVICE_TYPE, db)):
        return dependencies.device_error()

    db_lightState = models.LightSocket(state= lightState.state, 
                                device_id= deviceId,
                                createdDate=createdDate,
                                owner_id=user_id)
    db.add(db_lightState)
    db.commit()
    db.refresh(db_lightState)

    '''
        Connect to esp and send POST to change value
    '''

    ip_address = dependencies.get_ip_from_id(deviceId, user_id, DEVICE_TYPE, db)
    post_endpoint = dependencies.get_post_endpoint_from_id(deviceId, user_id, DEVICE_TYPE, db)
    url =  ip_address + post_endpoint
    data = lightState
    response = dependencies.send_data_to_esp(url, data)
    if(response == 500 or response.status > 400):
        return dependencies.esp_error(response)
    
    
    return db_lightState
