from sqlalchemy import Column, Integer, String, Text, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from .base import TimestampedModel

class Tour(TimestampedModel):
    __tablename__ = "tours"

    name = Column(String, nullable=False)
    description = Column(Text)
    destination = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    price_per_guest = Column(Numeric(10, 2), nullable=False)
    max_capacity = Column(Integer)
    current_bookings_count = Column(Integer, default=0) # Renamed from current_bookings to avoid confusion with relationship
    itinerary_details = Column(Text) # Can be Markdown or JSON from AI
    travel_mode = Column(String(50), nullable=True) # New field

    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    creator = relationship("User", back_populates="tours_created")

    bookings = relationship("Booking", back_populates="tour")
    hotel_allocations = relationship("TourHotelAllocation", back_populates="tour")
