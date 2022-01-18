from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas
import dependencies 
from fastapi import HTTPException
import json

DEVICE_TYPE = 'LED_STRIP'
STATE_ON = "On"
STATE_OFF = "Off"
STATE_DISCONNECTED = "Disconnected"

async def get_last_led_stripe_state(db: Session, deviceId: int, user_id: int):
    if(not dependencies.is_device_in_config(deviceId, user_id, DEVICE_TYPE, db)):
        return dependencies.device_error()

    response = await dependencies.check_is_esp_online(deviceId, user_id, DEVICE_TYPE, db)
    if response.status_code > 400:
        return dependencies.esp_error(response)

    db_obj = db.query(models.LedStrip).filter(models.LedStrip.device_id == deviceId).order_by(models.LedStrip.id.desc()).first()
    if not db_obj:
        return schemas.LedStripBase(state = STATE_OFF,
                                        color_red = 0,
                                        color_green = 0,
                                        color_blue = 0)

    serialized_response = json.loads(response.data)
    serialized_response_state = serialized_response['state']
    serialized_response_color_red = serialized_response['color_red']
    serialized_response_color_green = serialized_response['color_green']
    serialized_response_color_blue = serialized_response['color_blue']
    if(db_obj.state != serialized_response_state):
        state_to_return = schemas.LedStripBase(state = STATE_ON if serialized_response_state else STATE_OFF,
                                                color_red = serialized_response_color_red,
                                                color_green = serialized_response_color_green,
                                                color_blue = serialized_response_color_blue)
        createdDate = datetime.now() 
        db_LedStripState = models.LedStrip(state= serialized_response_state, 
                                           device_id= deviceId,
                                            color_red = serialized_response_color_red,
                                            color_green = serialized_response_color_green,
                                            color_blue = serialized_response_color_blue,
                                            createdDate=createdDate,
                                            owner_id=user_id)
        db.add(db_LedStripState)
        db.commit()
        db.refresh(db_LedStripState)
        return state_to_return
    return schemas.LedStripBase(state = STATE_ON if db_obj.state else STATE_OFF,
                                                color_red = db_obj.color_red,
                                                color_green = db_obj.color_green,
                                                color_blue = db_obj.color_blue)

def get_last_led_stripe_state_for_device(db: Session, deviceIp: str):
    deviceId = dependencies.get_id_from_ip(deviceIp, DEVICE_TYPE, db)

    db_obj = db.query(models.LedStrip).filter(models.LedStrip.device_id == deviceId).order_by(models.LedStrip.id.desc()).first()
    if not db_obj:
        return schemas.LedStripBase(state = STATE_OFF,
                                    color_red = 0,
                                    color_green = 0,
                                    color_blue = 0)
    state_to_return = schemas.LedStripBase(state = STATE_ON if db_obj.state else STATE_OFF,
                                            color_red = db_obj.color_red,
                                            color_green = db_obj.color_green,
                                            color_blue = db_obj.color_blue)
    return state_to_return

async def create_led_stripe_state(db: Session, ledStripState: schemas.LedStripCreate, user_id: int, deviceId: int):
    createdDate = datetime.now()
    if(not dependencies.is_device_in_config(deviceId, user_id, DEVICE_TYPE, db)):
        return dependencies.device_error()
        
    db_LedStripState = models.LedStrip(state= ledStripState.state, 
                                    device_id= deviceId,
                                    color_red = ledStripState.color_red,
                                    color_green = ledStripState.color_green,
                                    color_blue = ledStripState.color_blue,
                                    createdDate=createdDate,
                                    owner_id=user_id)
    db.add(db_LedStripState)
    db.commit()
    db.refresh(db_LedStripState)

    '''
        Connect to esp and send POST to change value
    '''
    ip_address = dependencies.get_ip_from_id(deviceId, user_id, DEVICE_TYPE, db)
    post_endpoint = dependencies.get_post_endpoint_from_id(deviceId, user_id, DEVICE_TYPE, db)
    url =  ip_address + post_endpoint
    data = ledStripState.toJson()
    response = await dependencies.send_data_to_esp(url, data)
    if(response.status_code > 400):
        return dependencies.esp_error(response)

    return db_LedStripState
