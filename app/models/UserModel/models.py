from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)

    acSockets = relationship("AcSocket", back_populates="owner")
    lightSockets = relationship("LightSocket", back_populates="owner")
    ledStrips = relationship("LedStrip", back_populates="owner")
    temperatureHumidities = relationship("TemperatureHumidity", back_populates="owner")