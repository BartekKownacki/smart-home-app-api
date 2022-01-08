from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database import Base

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    type = Column(String)
    ip_address = Column(String)
    post_endpoint = Column(String)
    get_endpoint = Column(String)

    owner_id = Column(Integer, ForeignKey("users.id"))

    acSockets = relationship("AcSocket", back_populates="device")
    lightSockets = relationship("LightSocket", back_populates="device")
    ledStrips = relationship("LedStrip", back_populates="device")
    temperatureHumidities = relationship("TemperatureHumidity", back_populates="device")


