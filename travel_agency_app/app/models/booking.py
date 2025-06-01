from sqlalchemy import Column, Integer, String, Text, Date, Numeric, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from .base import TimestampedModel

class Booking(TimestampedModel):
    __tablename__ = "bookings"

    guest_id = Column(Integer, ForeignKey("guests.id"), nullable=False)
    tour_id = Column(Integer, ForeignKey("tours.id"), nullable=True) # Nullable for standalone hotel bookings
    booking_date = Column(DateTime, default=func.now(), nullable=False)
    number_of_guests = Column(Integer, nullable=False, default=1)
    total_price = Column(Numeric(10, 2), nullable=False)
    status = Column(String, nullable=False, default='Pending') # e.g., 'Pending', 'Confirmed', 'Cancelled', 'Paid'
    notes = Column(Text)

    guest = relationship("Guest", back_populates="bookings")
    tour = relationship("Tour", back_populates="bookings")
    payments = relationship("Payment", back_populates="booking")
    room_assignments = relationship("BookingRoomAssignment", back_populates="booking")

class TourHotelAllocation(TimestampedModel):
    __tablename__ = "tour_hotel_allocations"

    tour_id = Column(Integer, ForeignKey("tours.id"), nullable=False)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)
    room_configuration_id = Column(Integer, ForeignKey("room_configurations.id"), nullable=False)
    allocated_rooms = Column(Integer, nullable=False)
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=False)

    tour = relationship("Tour", back_populates="hotel_allocations")
    hotel = relationship("Hotel", back_populates="tour_allocations")
    room_configuration = relationship("RoomConfiguration", back_populates="tour_allocations")
    booking_assignments = relationship("BookingRoomAssignment", back_populates="tour_hotel_allocation")
    # Add UniqueConstraint(("tour_id", "hotel_id", "room_configuration_id"), name="uix_tour_hotel_room_config") in actual DB migration

class BookingRoomAssignment(TimestampedModel):
    __tablename__ = "booking_room_assignments"

    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    tour_hotel_allocation_id = Column(Integer, ForeignKey("tour_hotel_allocations.id"), nullable=False)
    assigned_room_count = Column(Integer, nullable=False, default=1)
    room_details = Column(String, nullable=True) # e.g., "Room 101, Room 102"

    booking = relationship("Booking", back_populates="room_assignments")
    tour_hotel_allocation = relationship("TourHotelAllocation", back_populates="booking_assignments")
