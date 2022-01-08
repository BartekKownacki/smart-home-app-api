from typing import List, Optional
from datetime import datetime, timedelta

from models.LightSocketModel import crud, schemas
import dependencies
from database import SessionLocal, engine
from sqlalchemy.orm import Session

from fastapi import Depends, FastAPI, HTTPException, status, APIRouter, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse

router = APIRouter(
    prefix="/lightswitch",
    tags=["Light Switch actions"],
    responses={404: {"description": "Not found"}},
)

#For device
@router.get("/getLastState/device", response_model=schemas.LightSocketBase)
def get_last_light_socket_state_for_registered_device(request: Request,db: Session = Depends(dependencies.get_db)):
    device_is_registered = dependencies.is_ip_in_config(request,db)
    deviceIp = dependencies.get_request_ip(request)
    if(device_is_registered):
        state = crud.get_last_light_state_for_device(db, deviceIp)
        return state
    return HTTPException(status_code=403, detail="device not registered")

@router.get("/getLastState/{deviceId}", response_model=schemas.LightSocketBase)
async def get_last_light_socket_state(deviceId:int, db: Session = Depends(dependencies.get_db), current_user_id: int = Depends(dependencies.get_current_user_id)):
    state = await crud.get_last_light_state(db, deviceId, current_user_id)
    return state

@router.post("/createState/{deviceId}", response_model=schemas.LightSocket)
async def create_new_light_socket_state(deviceId: int, lightState: schemas.LightSocketCreate, db: Session = Depends(dependencies.get_db), current_user_id: int = Depends(dependencies.get_current_user_id)):
    return await crud.create_light_state(db=db, lightState=lightState, user_id=current_user_id, deviceId=deviceId)