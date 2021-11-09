from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database import Base

class LedStripe(Base):
    __tablename__ = "ledStripes"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(Boolean)
    color_red = Column(Integer)
    color_green = Column(Integer)
    color_blue = Column(Integer)
    createdDate = Column(DateTime)
    device_id = Column(Integer)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="ledStripes")