from typing import List, Optional
from datetime import datetime, timedelta

from models.TempHumidModel import crud, schemas
import dependencies
from database import SessionLocal, engine
from sqlalchemy.orm import Session

from models.UserModel import schemas as UserSchemas
from fastapi import Depends, FastAPI, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from fastapi_utils.tasks import repeat_every

router = APIRouter(
    prefix="/temphumid",
    tags=["Temperature and Humidity actions"],
    responses={404: {"description": "Not found"}},
)

@router.get("/getLastState", response_model=schemas.TemperatureHumidity)
def get_last_temphumid_state(db: Session = Depends(dependencies.get_db), current_user_id: int = Depends(dependencies.get_current_active_user_id)):
    state = crud.get_last_temperature_humidity_state(db)
    return state


# @router.get("/checkState/last", response_model=schemas.TemperatureHumidity)
# def get_last_state_from_esp(db: Session = Depends(dependencies.get_db), current_user_id: int = Depends(dependencies.get_current_active_user_id)):
#     return crud.create_new_temperature_humidity_state(db=db, action_type="last", user_id=current_user_id)

@repeat_every(seconds=60 * 60) 
def get_state_from_esp(db: Session = Depends(dependencies.get_db)):
    return crud.create_new_temperature_humidity_state(db=db, action_type="frequently", user_id=0)

@router.get("/checkState/now", response_model=schemas.TemperatureHumidity)
def get_last_state_from_esp(db: Session = Depends(dependencies.get_db), current_user_id: int = Depends(dependencies.get_current_active_user_id)):
    return crud.create_new_temperature_humidity_state(db=db, action_type="now", user_id=current_user_id)

@router.get("/getAll", response_model=List[schemas.TemperatureHumidity])
def get_all_temphumid_states(skip: int = 0, limit: int = 100, db: Session = Depends(dependencies.get_db), current_user: UserSchemas.User = Depends(dependencies.get_current_active_user)):
    users = crud.get_all_states(db, skip=skip, limit=limit)
    return users