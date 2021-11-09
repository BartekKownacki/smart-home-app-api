from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas
import dependencies 
from fastapi import HTTPException

DEVICE_TYPE = 'TEMPHUMID'

def get_last_temperature_humidity_state(db: Session):
    return db.query(models.TemperatureHumidity).order_by(models.TemperatureHumidity.id.desc()).first()

def get_data_from_esp_now(db: Session, user_id: int, temphumid):
    '''
        Get data from esp and save to db
    '''
    return create_new_temperature_humidity_state(db, user_id, temphumid)

def create_new_temperature_humidity_state(db: Session, user_id: int, temphumid: schemas.TemperatureHumidityCreate ):
    createdDate = datetime.now()
    print(user_id)

    device_id = dependencies.get_id_from_ip(temphumid.device_ip, DEVICE_TYPE)
    if(device_id == 0 or not dependencies.is_device_in_config(device_id, DEVICE_TYPE)):
        return dependencies.device_error()
    print(type(device_id))
    db_tempdhumidState = models.TemperatureHumidity(temperature = temphumid.temperature,
                                humidity = temphumid.humidity,
                                createdDate=createdDate,
                                device_id=device_id,
                                owner_id=user_id)

    db.add(db_tempdhumidState)
    db.commit()
    db.refresh(db_tempdhumidState)

    return db_tempdhumidState

def get_all_states(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TemperatureHumidity).offset(skip).limit(limit).all()