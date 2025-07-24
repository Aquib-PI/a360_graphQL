from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.orm import relationship

from .base import Base

class Acquirer(Base):
    __tablename__ = "acquirer"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(Text, nullable=False)
    created_at  = Column(DateTime, nullable=False)

    transactions = relationship("LiveTransaction", back_populates="acquirer") 