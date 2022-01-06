from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas
import dependencies 
from fastapi import HTTPException

DEVICE_TYPE = 'LED_STRIPE'

def get_last_led_stripe_state(db: Session, deviceId: int):
    if(not dependencies.is_device_in_config(deviceId, DEVICE_TYPE)):
        return dependencies.device_error()

    db_obj = db.query(models.LedStripe).filter(models.LedStripe.device_id == deviceId).order_by(models.LedStripe.id.desc()).first()
    state_to_return = schemas.LedStripeBase(device_id = db_obj.device_id,
                                                state = db_obj.state,
                                                color_red = db_obj.color_red,
                                                color_green = db_obj.color_green,
                                                color_blue = db_obj.color_blue)
    return state_to_return

def get_last_led_stripe_state_for_device(db: Session, deviceIp: str):
    deviceId = dependencies.get_id_from_ip(deviceIp, DEVICE_TYPE)
    if(not dependencies.is_device_in_config(deviceId, DEVICE_TYPE)):
        return dependencies.device_error()

    db_obj = db.query(models.LedStripe).filter(models.LedStripe.device_id == deviceId).order_by(models.LedStripe.id.desc()).first()
    state_to_return = schemas.LedStripeBase(device_id = db_obj.device_id,
                                                state = db_obj.state,
                                                color_red = db_obj.color_red,
                                                color_green = db_obj.color_green,
                                                color_blue = db_obj.color_blue)
    return state_to_return

def create_led_stripe_state(db: Session, ledStripeState: schemas.LedStripeCreate, user_id: int):
    createdDate = datetime.now()

    if(not dependencies.is_device_in_config(ledStripeState.device_id, DEVICE_TYPE)):
        return dependencies.device_error()
        
    db_ledStripeState = models.LedStripe(state= ledStripeState.state, 
                                    device_id= ledStripeState.device_id,
                                    color_red = ledStripeState.color_red,
                                    color_green = ledStripeState.color_green,
                                    color_blue = ledStripeState.color_blue,
                                    createdDate=createdDate,
                                    owner_id=user_id)
    db.add(db_ledStripeState)
    db.commit()
    db.refresh(db_ledStripeState)

    '''
        Connect to esp and send POST to change value
    '''
    ip_address = dependencies.get_ip_from_id(ledStripeState.device_id, DEVICE_TYPE)
    post_endpoint = dependencies.get_endpoint_from_id(ledStripeState.device_id, DEVICE_TYPE, "post")
    url =  ip_address + post_endpoint
    data = ledStripeState
    response = dependencies.send_data_to_esp(url, data)
    if(response.status > 400):
        return dependencies.esp_error(response)

    return db_ledStripeState
