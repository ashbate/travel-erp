from sqlalchemy import Column, Integer, String, Date, Text
from sqlalchemy.orm import relationship
from .base import TimestampedModel

class Guest(TimestampedModel):
    __tablename__ = "guests"

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, nullable=True) # Assuming phone_number can be optional
    date_of_birth = Column(Date, nullable=True) # Assuming date_of_birth can be optional
    # passport_info = Column(String) # Removed
    preferences = Column(Text, nullable=True) # Assuming preferences can be optional

    # New passport fields
    passport_number = Column(String(100), nullable=True, index=True)
    passport_expiry_date = Column(Date, nullable=True)
    passport_issuing_country = Column(String(100), nullable=True)
    visa_details = Column(Text, nullable=True) # New field for visa details

    bookings = relationship("Booking", back_populates="guest")
