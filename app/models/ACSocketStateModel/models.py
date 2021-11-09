from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database import Base

class AcSocket(Base):
    __tablename__ = "acSockets"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(Boolean)
    timeStampToTurnOn = Column(DateTime, nullable=True)
    timeStampToTurnOff = Column(DateTime, nullable=True)
    createdDate = Column(DateTime)
    device_id = Column(Integer)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="acSockets")


