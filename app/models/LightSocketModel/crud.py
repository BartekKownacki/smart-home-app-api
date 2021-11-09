from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas
import dependencies 
from fastapi import HTTPException

DEVICE_TYPE = 'LIGHT_BULB'

def get_last_light_state(db: Session, deviceId: int):
    if(not dependencies.is_device_in_config(deviceId, DEVICE_TYPE)):
        return dependencies.device_error()
    return db.query(models.LightSocket).order_by(models.LightSocket.id.desc()).first()

def create_light_state(db: Session, lightState: schemas.LightSocketCreate, user_id: int):
    createdDate = datetime.now()
    if(not dependencies.is_device_in_config(lightState.device_id, DEVICE_TYPE)):
        return dependencies.device_error()

    db_lightState = models.LightSocket(state= lightState.state, 
                                device_id= lightState.device_id,
                                timeStampToTurnOn = lightState.timeStampToTurnOn,
                                timeStampToTurnOff = lightState.timeStampToTurnOff,
                                createdDate=createdDate,
                                owner_id=user_id)
    db.add(db_lightState)
    db.commit()
    db.refresh(db_lightState)

    '''
        Connect to esp and send POST to change value
    '''
    return db_lightState
