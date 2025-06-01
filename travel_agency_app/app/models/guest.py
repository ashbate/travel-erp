from sqlalchemy import Column, Integer, String, Date, Text
from sqlalchemy.orm import relationship
from .base import TimestampedModel

class Guest(TimestampedModel):
    __tablename__ = "guests"

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String)
    date_of_birth = Column(Date)
    passport_info = Column(String) # Consider JSON or a separate table if complex
    preferences = Column(Text) # Special requests, dietary needs

    bookings = relationship("Booking", back_populates="guest")
