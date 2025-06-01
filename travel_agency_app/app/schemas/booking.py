from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from .base import BaseSchema, TimestampedSchema
from .guest import GuestRead
from .tour import TourRead

# --- BookingRoomAssignment Schemas ---
class BookingRoomAssignmentBase(BaseSchema):
    tour_hotel_allocation_id: int
    assigned_room_count: int = 1
    room_details: Optional[str] = None

class BookingRoomAssignmentCreate(BookingRoomAssignmentBase):
   pass # booking_id will be path param or in service

class BookingRoomAssignmentUpdate(BaseSchema):
    assigned_room_count: Optional[int] = None
    room_details: Optional[str] = None

class BookingRoomAssignmentRead(BookingRoomAssignmentBase, TimestampedSchema):
    booking_id: int

# --- Booking Schemas ---
class BookingBase(BaseSchema):
    guest_id: int
    tour_id: Optional[int] = None # For standalone hotel bookings
    number_of_guests: int = 1
    status: str = 'Pending'
    notes: Optional[str] = None

class BookingCreate(BookingBase):
    # total_price might be calculated in the service
    pass

class BookingUpdate(BaseSchema):
    number_of_guests: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    # total_price update might be restricted or handled by specific actions

class BookingRead(BookingBase, TimestampedSchema):
    total_price: Decimal
    booking_date: datetime
    guest: Optional[GuestRead] = None
    tour: Optional[TourRead] = None
    room_assignments: List[BookingRoomAssignmentRead] = []
