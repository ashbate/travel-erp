from typing import Optional
from datetime import date
from .base import BaseSchema, TimestampedSchema

class GuestBase(BaseSchema):
    first_name: str
    last_name: str
    email: str
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    # passport_info: Optional[str] = None # Removed
    preferences: Optional[str] = None
    passport_number: Optional[str] = None
    passport_expiry_date: Optional[date] = None
    passport_issuing_country: Optional[str] = None
    visa_details: Optional[str] = None

class GuestCreate(GuestBase):
    pass

class GuestUpdate(BaseSchema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    # passport_info: Optional[str] = None # Removed
    preferences: Optional[str] = None
    passport_number: Optional[str] = None
    passport_expiry_date: Optional[date] = None
    passport_issuing_country: Optional[str] = None
    visa_details: Optional[str] = None

class GuestRead(GuestBase, TimestampedSchema):
    pass
