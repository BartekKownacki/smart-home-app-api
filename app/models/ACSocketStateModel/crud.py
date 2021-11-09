from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas
import dependencies 
from fastapi import HTTPException

DEVICE_TYPE = 'AC_SOCKET'

def get_last_ac_state(db: Session, deviceId: int):
    if(not dependencies.is_device_in_config(deviceId, DEVICE_TYPE)):
        return dependencies.device_error()
    return db.query(models.AcSocket).filter(models.AcSocket.device_id == deviceId).order_by(models.AcSocket.id.desc()).first()

def create_ac_state(db: Session, acState: schemas.AcSocketCreate, user_id: int):
    createdDate = datetime.now()

    if(not dependencies.is_device_in_config(acState.device_id, DEVICE_TYPE)):
        return dependencies.device_error()

    db_acState = models.AcSocket(state= acState.state, 
                                device_id= acState.device_id,
                                timeStampToTurnOn = acState.timeStampToTurnOn,
                                timeStampToTurnOff = acState.timeStampToTurnOff,
                                createdDate=createdDate,
                                owner_id=user_id)
    db.add(db_acState)
    db.commit()
    db.refresh(db_acState)

    '''
        Connect to esp and send POST to change value
    '''
    return db_acState





