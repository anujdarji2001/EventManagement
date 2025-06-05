# Pydantic schemas will be defined here
from _testcapi import INT_MAX
from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
from datetime import datetime
import pytz

IST = pytz.timezone('Asia/Kolkata')
UTC = pytz.UTC

class EventBase(BaseModel):
    name: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)
    start_time: datetime
    end_time: datetime
    max_capacity: int = Field(..., gt=0)

    @validator('max_capacity')
    def validate_max_capacity(cls, v):
        if v > INT_MAX:
            raise ValueError(f"max_capacity cannot exceed {INT_MAX}")
        if v <= 0:  # Though Field(gt=0) already covers this
            raise ValueError("max_capacity must be a positive number")
        return v

    @validator('start_time', 'end_time', pre=True)
    def ensure_timezone(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            v = datetime.fromisoformat(v)
        if isinstance(v, datetime):
            if v.tzinfo is None:
                return IST.localize(v)
            return v.astimezone(UTC)  # Store in UTC
        return v

class EventCreate(EventBase):
    pass

class EventOut(EventBase):
    id: int
    class Config:
        from_attributes = True

class PaginatedEvents(BaseModel):
    total: int
    page: int
    size: int
    events: List[EventOut]

class AttendeeBase(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr

class AttendeeCreate(AttendeeBase):
    pass

class AttendeeOut(AttendeeBase):
    id: int
    class Config:
        from_attributes = True

class RegistrationCreate(BaseModel):
    name: str
    email: EmailStr

class RegistrationOut(BaseModel):
    id: int
    event_id: int
    attendee_id: int
    class Config:
        from_attributes = True

class PaginatedAttendees(BaseModel):
    total: int
    page: int
    size: int
    attendees: List[AttendeeOut] 