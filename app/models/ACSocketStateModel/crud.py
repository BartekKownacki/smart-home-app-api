from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas


def get_last_ac_state(db: Session):
    return db.query(models.AcSocket).order_by(models.AcSocket.id.desc()).first()

def create_ac_state(db: Session, acState: schemas.AcSocketCreate, user_id: int):
    createdDate = datetime.now()
    print(user_id)
    db_acState = models.AcSocket(state= acState.state, 
                                timeStampToTurnOn = acState.timeStampToTurnOn,
                                timeStampToTurnOff = acState.timeStampToTurnOff,
                                createdDate=createdDate,
                                owner_id=user_id)
    db.add(db_acState)
    db.commit()
    db.refresh(db_acState)

    '''
        Connect to esp and send POST to change value
    '''
    return db_acState





