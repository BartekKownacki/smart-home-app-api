from typing import List, Optional
from datetime import datetime, timedelta

from models.ACSocketStateModel import crud, schemas
import dependencies
from database import SessionLocal, engine
from sqlalchemy.orm import Session

from fastapi import Depends, FastAPI, HTTPException, status, APIRouter, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse

router = APIRouter(
    prefix="/acsocket",
    tags=["AC Socket actions"],
    responses={404: {"description": "Not found"}},
)

@router.get("/getLastState/{deviceId}", response_model=schemas.AcSocket)
def get_last_ac_state(deviceId:int, db: Session = Depends(dependencies.get_db), current_user_id: int = Depends(dependencies.get_current_user_id)):
    state = crud.get_last_ac_state(db, deviceId)
    return state

@router.get("/getLastState/{deviceId}/device", response_model=schemas.AcSocket)
def get_last_ac_state_for_registered_device(deviceId:int, request: Request,db: Session = Depends(dependencies.get_db), device_is_registered: str = Depends(dependencies.get_current_request_ip)):
    if(device_is_registered):
        state = crud.get_last_ac_state(db, deviceId)
        return state
    return HTTPException(status_code=403, detail="device not registered")

@router.post("/createState", response_model=schemas.AcSocket)
def create_new_ac_state(acState: schemas.AcSocketCreate, db: Session = Depends(dependencies.get_db), current_user_id: int = Depends(dependencies.get_current_user_id)):
    return crud.create_ac_state(db=db, acState=acState, user_id=current_user_id)