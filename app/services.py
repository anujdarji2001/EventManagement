# Business logic and service functions will be defined here 

from app import crud
from app.schemas import EventCreate, AttendeeCreate, RegistrationCreate, PaginatedAttendees, AttendeeOut, EventOut
from app.models import Event
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import List, Optional
import pytz
from datetime import datetime

IST = pytz.timezone('Asia/Kolkata')
UTC = pytz.UTC

def ensure_utc(dt: datetime) -> datetime:
    """Ensure datetime is in UTC."""
    if dt.tzinfo is None:
        return UTC.localize(dt)
    return dt.astimezone(UTC)

def convert_to_timezone(dt: datetime, target_timezone: str) -> datetime:
    """Convert datetime to target timezone."""
    if dt.tzinfo is None:
        dt = UTC.localize(dt)
    target_tz = pytz.timezone(target_timezone)
    return dt.astimezone(target_tz)

async def create_event_service(db: AsyncSession, event: EventCreate):
    # Convert times to UTC before storing
    event_dict = event.dict()
    event_dict['start_time'] = ensure_utc(event.start_time)
    event_dict['end_time'] = ensure_utc(event.end_time)
    return await crud.create_event(db, EventCreate(**event_dict))

async def list_events_service(db: AsyncSession, timezone: Optional[str] = 'Asia/Kolkata'):
    events = await crud.get_events(db)
    # Convert times to requested timezone
    events_out = []
    for event in events:
        event_out = EventOut.from_orm(event)
        # Convert UTC times to target timezone
        event_out.start_time = convert_to_timezone(event_out.start_time, timezone)
        event_out.end_time = convert_to_timezone(event_out.end_time, timezone)
        events_out.append(event_out)
    return events_out

async def register_attendee_service(db: AsyncSession, event_id: int, reg: RegistrationCreate):
    event = await crud.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    attendee = await crud.get_attendee_by_email(db, reg.email)
    if not attendee:
        attendee = await crud.create_attendee(db, AttendeeCreate(name=reg.name, email=reg.email))
    try:
        registration = await crud.register_attendee(db, event, attendee)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return registration

async def get_attendees_service(db: AsyncSession, event_id: int, page: int = 1, size: int = 10) -> PaginatedAttendees:
    event = await crud.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    skip = (page - 1) * size
    attendees = await crud.get_attendees_for_event(db, event_id, skip=skip, limit=size)
    total = await crud.count_attendees_for_event(db, event_id)
    attendees_out = [AttendeeOut.from_orm(a) for a in attendees]
    return PaginatedAttendees(
        total=total,
        page=page,
        size=size,
        attendees=attendees_out
    ) 