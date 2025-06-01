from typing import Optional, List
from datetime import date
from decimal import Decimal
from .base import BaseSchema, TimestampedSchema
from .user import UserRead
from .hotel import RoomConfigurationRead # For tour hotel allocations

# --- TourHotelAllocation Schemas ---
class TourHotelAllocationBase(BaseSchema):
    hotel_id: int
    room_configuration_id: int
    allocated_rooms: int
    check_in_date: date
    check_out_date: date

class TourHotelAllocationCreate(TourHotelAllocationBase):
    pass # tour_id will be path param or in service

class TourHotelAllocationUpdate(BaseSchema):
    allocated_rooms: Optional[int] = None
    check_in_date: Optional[date] = None
    check_out_date: Optional[date] = None

class TourHotelAllocationRead(TourHotelAllocationBase, TimestampedSchema):
    tour_id: int
    # Potentially add nested HotelRead and RoomConfigurationRead if needed for responses

# --- Tour Schemas ---
class TourBase(BaseSchema):
    name: str
    description: Optional[str] = None
    destination: str
    start_date: date
    end_date: date
    price_per_guest: Decimal
    max_capacity: Optional[int] = None
    itinerary_details: Optional[str] = None

class TourCreate(TourBase):
    created_by_user_id: int

class TourUpdate(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    destination: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    price_per_guest: Optional[Decimal] = None
    max_capacity: Optional[int] = None
    itinerary_details: Optional[str] = None

class TourRead(TourBase, TimestampedSchema):
    created_by_user_id: int
    current_bookings_count: int = 0
    creator: Optional[UserRead] = None # Assuming UserRead schema exists
    hotel_allocations: List[TourHotelAllocationRead] = []

# --- AI Tour Generation Schemas ---
class AITourPrompt(BaseSchema):
    destination: str
    duration_days: int
    traveler_type: Optional[str] = None # e.g., 'solo', 'couple', 'family', 'friends'
    interests: Optional[List[str]] = None # e.g., ['history', 'adventure', 'food', 'relaxation']
    budget_level: Optional[str] = None # e.g., 'budget', 'mid-range', 'luxury'
    preferred_activities: Optional[List[str]] = None
    # Add any other fields that might be useful for the AI prompt

class AIGeneratedItinerary(BaseSchema):
    tour_name_suggestion: str
    suggested_description: str
    itinerary_details: str # This will be the detailed day-by-day plan from AI (e.g., Markdown)
    estimated_price_range: Optional[str] = None # e.g., "$1000 - $1500 per person"
    warnings: Optional[List[str]] = None # e.g., "Requires high fitness level"
