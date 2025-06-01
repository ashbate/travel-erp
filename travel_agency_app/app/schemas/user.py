from typing import Optional
from .base import BaseSchema, TimestampedSchema

class UserBase(BaseSchema):
    username: str
    email: str
    full_name: Optional[str] = None
    role: Optional[str] = 'agent'

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseSchema):
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None

class UserRead(UserBase, TimestampedSchema):
    pass
