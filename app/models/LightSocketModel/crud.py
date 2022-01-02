from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas
import dependencies 
from fastapi import HTTPException

DEVICE_TYPE = 'LIGHT_BULB'

def get_last_light_state(db: Session, deviceId: int):
    if(not dependencies.is_device_in_config(deviceId, DEVICE_TYPE)):
        return dependencies.device_error()
    
    db_obj = db.query(models.LightSocket).filter(models.LightSocket.device_id == deviceId).order_by(models.LightSocket.id.desc()).first()
    state_to_return = schemas.LightSocketBase(device_id = db_obj.device_id,
                                                state = db_obj.state,)
    return state_to_return


def create_light_state(db: Session, lightState: schemas.LightSocketCreate, user_id: int):
    createdDate = datetime.now()
    if(not dependencies.is_device_in_config(lightState.device_id, DEVICE_TYPE)):
        return dependencies.device_error()

    db_lightState = models.LightSocket(state= lightState.state, 
                                device_id= lightState.device_id,
                                # timeStampToTurnOn = lightState.timeStampToTurnOn,
                                # timeStampToTurnOff = lightState.timeStampToTurnOff,
                                createdDate=createdDate,
                                owner_id=user_id)
    db.add(db_lightState)
    db.commit()
    db.refresh(db_lightState)

    '''
        Connect to esp and send POST to change value
    '''

    ip_address = dependencies.get_ip_from_id(lightState.device_id, DEVICE_TYPE)
    post_endpoint = dependencies.get_endpoint_from_id(lightState.device_id, DEVICE_TYPE, "post")
    url =  ip_address + post_endpoint
    data = lightState
    response = dependencies.send_data_to_esp(url, data)
    print(response)
    if(response.status > 400):
        return dependencies.esp_error(response)
    
    
    return db_lightState
