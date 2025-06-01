from typing import Optional, List
from decimal import Decimal
from .base import BaseSchema, TimestampedSchema

# --- RoomConfiguration Schemas ---
class RoomConfigurationBase(BaseSchema):
    room_type: str
    description: Optional[str] = None
    max_occupancy: int
    price_per_night: Decimal
    number_of_available_rooms: int

class RoomConfigurationCreate(RoomConfigurationBase):
    hotel_id: int # Required when creating

class RoomConfigurationUpdate(BaseSchema):
    room_type: Optional[str] = None
    description: Optional[str] = None
    max_occupancy: Optional[int] = None
    price_per_night: Optional[Decimal] = None
    number_of_available_rooms: Optional[int] = None

class RoomConfigurationRead(RoomConfigurationBase, TimestampedSchema):
    hotel_id: int

# --- Hotel Schemas ---
class HotelBase(BaseSchema):
    name: str
    address: str
    city: str
    country: str
    star_rating: Optional[int] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None

class HotelCreate(HotelBase):
    pass

class HotelUpdate(BaseSchema):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    star_rating: Optional[int] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None

class HotelRead(HotelBase, TimestampedSchema):
    room_configurations: List[RoomConfigurationRead] = []
