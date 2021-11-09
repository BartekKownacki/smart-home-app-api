from sqlalchemy.orm import Session
from sqlalchemy import update
from . import models, schemas
import dependencies


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    db_user = db.query(models.User).filter(models.User.username == username).first()

    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def change_user_role(db: Session, username: str, value: bool):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return False
    db.query(models.User).filter(models.User.username == username).update({'is_admin': value})
    db.commit()
    return username

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = dependencies.get_hashed_password(user.password)
    db_user = models.User(username=user.username,
                          email=user.email, 
                          hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
