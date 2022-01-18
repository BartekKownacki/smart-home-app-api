from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas
import dependencies 
from fastapi import HTTPException
import json
DEVICE_TYPE = 'TEMP_HUMID'

def get_last_temperature_humidity_state(db: Session, deviceId: int, user_id: int):
    if(not dependencies.is_device_in_config(deviceId, user_id, DEVICE_TYPE, db)):
        return dependencies.device_error()
    db_obj = db.query(models.TemperatureHumidity).filter(models.TemperatureHumidity.device_id == deviceId).order_by(models.TemperatureHumidity.id.desc()).first()
    
    if not db_obj:
        return schemas.TemperatureHumidityBase(temperature = 0,
                                                    humidity = 0)
    
    state_to_return = schemas.TemperatureHumidityBase(temperature = db_obj.temperature,
                                                        humidity = db_obj.humidity)
    return state_to_return


async def get_data_from_esp_now(db: Session, user_id: int, device_id):
    ip_address = dependencies.get_ip_from_id(device_id, user_id, DEVICE_TYPE, db)
    get_endpoint = dependencies.get_get_endpoint_from_id(device_id, user_id, DEVICE_TYPE, db)
    url =  ip_address + get_endpoint
    response = await dependencies.get_data_from_esp(url)
    if(response.status_code > 400):
         return dependencies.esp_error(response)

    serialized_response = json.loads(response.data)
    serialized_response_temperature = serialized_response['temperature']
    serialized_response_humidity = serialized_response['humidity']
    temphumid = schemas.TemperatureHumidityBase(temperature= serialized_response_temperature,
                                                    humidity= serialized_response_humidity)    
    
    # work with response
    createdDate = datetime.now()
    db_tempdhumidState = models.TemperatureHumidity(temperature = temphumid.temperature,
                                humidity = temphumid.humidity,
                                createdDate=createdDate,
                                device_id=device_id,
                                owner_id=user_id)
    db.add(db_tempdhumidState)
    db.commit()
    db.refresh(db_tempdhumidState)
    
    return temphumid

def create_new_temperature_humidity_state(db: Session, user_id: int, temphumid: schemas.TemperatureHumidityCreate ):
    createdDate = datetime.now()

    device_id = dependencies.get_id_from_ip(temphumid.device_ip, DEVICE_TYPE, db)
    if(device_id == 0 or not dependencies.is_device_in_config(device_id, user_id, DEVICE_TYPE, db)):
        return dependencies.device_error()
    db_tempdhumidState = models.TemperatureHumidity(temperature = temphumid.temperature,
                                humidity = temphumid.humidity,
                                createdDate=createdDate,
                                device_id=device_id,
                                owner_id=user_id)

    db.add(db_tempdhumidState)
    db.commit()
    db.refresh(db_tempdhumidState)
    temphumidState_to_return = schemas.TemperatureHumidityBase(temperature= db_tempdhumidState.temperature,
                                                                humidity= db_tempdhumidState.humidity)

    return temphumidState_to_return
