from typing import List, Optional
from datetime import datetime, timedelta

from models.LedStripeModel import crud, schemas
import dependencies
from database import SessionLocal, engine
from sqlalchemy.orm import Session

from fastapi import Depends, FastAPI, HTTPException, status, APIRouter, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse

router = APIRouter(
    prefix="/LedStripe",
    tags=["Led Stripe actions"],
    responses={404: {"description": "Not found"}},
)

#For device
@router.get("/getLastState/device", response_model=schemas.LedStripeBase)
def get_last_led_stripe_state_for_registered_device(request: Request,db: Session = Depends(dependencies.get_db), device_is_registered: str = Depends(dependencies.is_ip_in_config)):
    deviceIp = dependencies.get_request_ip(request)
    print(deviceIp)
    if(device_is_registered):
        state = crud.get_last_led_stripe_state_for_device(db, deviceIp)
        return state
    return HTTPException(status_code=403, detail="device not registered")

@router.get("/getLastState/{deviceId}", response_model=schemas.LedStripeBase)
def get_last_led_stripe_state(deviceId:int, db: Session = Depends(dependencies.get_db), current_user_id: int = Depends(dependencies.get_current_user_id)):
    state = crud.get_last_led_stripe_state(db, deviceId)
    return state

@router.post("/createState", response_model=schemas.LedStripe)
def create_led_stripe_state(ledStripeState: schemas.LedStripeCreate, db: Session = Depends(dependencies.get_db), current_user_id: int = Depends(dependencies.get_current_user_id)):
    return crud.create_led_stripe_state(db=db, ledStripeState=ledStripeState, user_id=current_user_id)