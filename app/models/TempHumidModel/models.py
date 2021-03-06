from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship
from database import Base

class TemperatureHumidity(Base):
    __tablename__ = "temperatureHumidities"

    id = Column(Integer, primary_key=True, index=True)
    temperature = Column(Float)
    humidity = Column(Integer)
    createdDate = Column(DateTime)
    device_id = Column(Integer, ForeignKey("devices.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="temperatureHumidities")
    device = relationship("Device", back_populates="temperatureHumidities")