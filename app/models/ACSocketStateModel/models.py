from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database import Base

class AcSocket(Base):
    __tablename__ = "acSockets"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(Boolean)
    createdDate = Column(DateTime)
    device_id = Column(Integer, ForeignKey("devices.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="acSockets")
    device = relationship("Device", back_populates="acSockets")

