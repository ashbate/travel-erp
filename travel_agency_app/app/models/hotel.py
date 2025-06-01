from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from .base import TimestampedModel

class Hotel(TimestampedModel):
    __tablename__ = "hotels"

    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    star_rating = Column(Integer)
    contact_email = Column(String)
    contact_phone = Column(String)

    room_configurations = relationship("RoomConfiguration", back_populates="hotel")
    tour_allocations = relationship("TourHotelAllocation", back_populates="hotel")

class RoomConfiguration(TimestampedModel):
    __tablename__ = "room_configurations"

    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)
    room_type = Column(String, nullable=False) # e.g., 'Single', 'Double', 'Suite'
    description = Column(Text)
    max_occupancy = Column(Integer, nullable=False)
    price_per_night = Column(Numeric(10, 2), nullable=False)
    number_of_available_rooms = Column(Integer, nullable=False)

    hotel = relationship("Hotel", back_populates="room_configurations")
    tour_allocations = relationship("TourHotelAllocation", back_populates="room_configuration")
