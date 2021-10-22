from typing import List, Optional
from datetime import datetime, timedelta

from models.LightSocketModel import crud, schemas
import dependencies
from database import SessionLocal, engine
from sqlalchemy.orm import Session

from fastapi import Depends, FastAPI, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse

router = APIRouter(
    prefix="/lightsocket",
    tags=["Light Socket actions"],
    responses={404: {"description": "Not found"}},
)

@router.get("/getLastState", response_model=schemas.LightSocket)
def get_last_ac_state(db: Session = Depends(dependencies.get_db), current_user_id: int = Depends(dependencies.get_current_active_user_id)):
    state = crud.get_last_light_state(db)
    return state

@router.post("/createState", response_model=schemas.LightSocket)
def create_new_ac_state(lightState: schemas.LightSocketCreate, db: Session = Depends(dependencies.get_db), current_user_id: int = Depends(dependencies.get_current_active_user_id)):
    return crud.create_light_state(db=db, lightState=lightState, user_id=current_user_id)