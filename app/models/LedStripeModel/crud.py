from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas


def get_last_led_stripe_state(db: Session):
    return db.query(models.LedStripe).order_by(models.LedStripe.id.desc()).first()

def create_led_stripe_state(db: Session, ledStripeState: schemas.LedStripeCreate, user_id: int):
    createdDate = datetime.now()
    print(user_id)
    db_ledStripeState = models.LedStripe(state= ledStripeState.state, 
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
    return db_ledStripeState
