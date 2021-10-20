from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database import Base

class Config(Base):
    __tablename__ = "AcSocket"

    id = Column(Integer, primary_key=True, index=True)
    state: Column(Boolean)
    timeStampToTurnOn: Column(DateTime, nullable=True)
    timeStampToTurnOff: Column(DateTime, nullable=True)
    createdDate: Column(DateTime)
    createdById: Column(Integer, ForeignKey("users.id"))
    

    User = relationship("User", back_populates="ac_socket")


