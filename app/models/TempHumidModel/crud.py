from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas


def get_last_temperature_humidity_state(db: Session):
    return db.query(models.TemperatureHumidity).order_by(models.TemperatureHumidity.id.desc()).first()

def get_data_from_esp_freqently():
    temperature = 0
    humidity = 0 
    return schemas.TemperatureHumidityCreate(temperature = temperature, humidity = humidity)

def get_data_from_esp_request():
    '''
        Get data from esp and save to db
    '''
    return schemas.TemperatureHumidityCreate()

def create_new_temperature_humidity_state(db: Session, action_type: str,  user_id: int):
    if (action_type == "frequently"):
        temphumid = get_data_from_esp_freqently()
    else:
        temphumid = get_data_from_esp_request()

    createdDate = datetime.now()
    print(user_id)
    db_tempdhumidState = models.TemperatureHumidity(temperature = temphumid.temperature,
                                humidity = temphumid.humidity,
                                createdDate=createdDate,
                                owner_id=user_id)
    db.add(db_tempdhumidState)
    db.commit()
    db.refresh(db_tempdhumidState)
    


    return db_tempdhumidState

def get_all_states(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TemperatureHumidity).offset(skip).limit(limit).all()