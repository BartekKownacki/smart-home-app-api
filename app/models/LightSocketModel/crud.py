from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas


def get_last_light_state(db: Session):
    return db.query(models.LightSocket).order_by(models.LightSocket.id.desc()).first()

def create_light_state(db: Session, lightState: schemas.LightSocketCreate, user_id: int):
    createdDate = datetime.now()
    print(user_id)
    db_lightState = models.LightSocket(state= lightState.state, 
                                timeStampToTurnOn = lightState.timeStampToTurnOn,
                                timeStampToTurnOff = lightState.timeStampToTurnOff,
                                createdDate=createdDate,
                                owner_id=user_id)
    db.add(db_lightState)
    db.commit()
    db.refresh(db_lightState)

    '''
        Connect to esp and send POST to change value
    '''
    return db_lightState
