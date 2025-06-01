from pydantic import BaseModel
from datetime import datetime

class BaseSchema(BaseModel):
    class Config:
        orm_mode = True
        from_attributes = True # For Pydantic v2, replaces orm_mode in some contexts

class TimestampedSchema(BaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime
