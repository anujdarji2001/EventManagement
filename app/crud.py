# CRUD operations for events and attendees will be defined here
from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Event, Attendee, Registration
from app.schemas import EventCreate, AttendeeCreate


async def create_event(db: AsyncSession, event: EventCreate) -> Event:
    db_event = Event(**event.dict())
    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)
    return db_event

async def get_events(db: AsyncSession) -> Sequence[Event]:
    result = await db.execute(select(Event).where(Event.start_time >= datetime.now()).order_by(Event.start_time))
    return result.scalars().all()

async def get_event(db: AsyncSession, event_id: int) -> Optional[Event]:
    result = await db.execute(select(Event).where(Event.id == event_id))
    return result.scalar_one_or_none()

async def get_attendee_by_email(db: AsyncSession, email: str) -> Optional[Attendee]:
    result = await db.execute(select(Attendee).where(Attendee.email == email))
    return result.scalar_one_or_none()

async def create_attendee(db: AsyncSession, attendee: AttendeeCreate) -> Attendee:
    db_attendee = Attendee(**attendee.dict())
    db.add(db_attendee)
    await db.commit()
    await db.refresh(db_attendee)
    return db_attendee

async def register_attendee(db: AsyncSession, event: Event, attendee: Attendee) -> Registration:
    # Check for overbooking
    result = await db.execute(select(func.count(Registration.id)).where(Registration.event_id == event.id))
    count = result.scalar()
    if count >= event.max_capacity:
        raise ValueError("Event is fully booked.")
    # Check for duplicate registration
    result = await db.execute(select(Registration).where(Registration.event_id == event.id, Registration.attendee_id == attendee.id))
    if result.scalar_one_or_none():
        raise ValueError("Attendee already registered for this event.")
    db_registration = Registration(event_id=event.id, attendee_id=attendee.id)
    db.add(db_registration)
    await db.commit()
    await db.refresh(db_registration)
    return db_registration

async def get_attendees_for_event(db: AsyncSession, event_id: int, skip: int = 0, limit: int = 10) -> Sequence[Attendee]:
    result = await db.execute(
        select(Attendee)
        .join(Registration, Registration.attendee_id == Attendee.id)
        .where(Registration.event_id == event_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def count_attendees_for_event(db: AsyncSession, event_id: int) -> int:
    result = await db.execute(
        select(func.count(Attendee.id))
        .join(Registration, Registration.attendee_id == Attendee.id)
        .where(Registration.event_id == event_id)
    )
    return result.scalar() 