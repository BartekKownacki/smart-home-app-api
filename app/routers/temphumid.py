from typing import List, Optional
from datetime import datetime, timedelta

from models.TempHumidModel import crud, schemas
import dependencies
from database import SessionLocal, engine
from sqlalchemy.orm import Session

from models.UserModel import schemas as UserSchemas
from fastapi import Depends, FastAPI, HTTPException, exceptions, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse

router = APIRouter(
    prefix="/temphumid",
    tags=["Temperature and Humidity actions"],
    responses={404: {"description": "Not found"}},
)

@router.get("/getLastState/{deviceId}", response_model=schemas.TemperatureHumidityBase)
def get_last_temphumid_state(deviceId:int, db: Session = Depends(dependencies.get_db), current_user_id: int = Depends(dependencies.get_current_user_id)):
    state = crud.get_last_temperature_humidity_state(db, deviceId, current_user_id)
    return state

@router.get("/checkState/{deviceId}/now", response_model=schemas.TemperatureHumidityBase)
async def get_last_state_from_esp(deviceId:int, db: Session = Depends(dependencies.get_db), current_user_id: int = Depends(dependencies.get_current_user_id)):
    return await crud.get_data_from_esp_now(db=db, user_id=current_user_id,device_id=deviceId )

@router.post("/saveState/device", response_model=schemas.TemperatureHumidityBase)
def post_states_from_esp_frequently_only_registered_ips(newState: schemas.TemperatureHumidityCreate, db: Session = Depends(dependencies.get_db)):
    device_is_registered = dependencies.is_ip_in_config(request,db)
    return crud.create_new_temperature_humidity_state(db=db, user_id=0, temphumid=newState)


