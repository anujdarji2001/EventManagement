from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import EventCreate, EventOut, PaginatedEvents
from app.services import create_event_service, list_events_service
from typing import List, Optional
import pytz

router = APIRouter(prefix="/events", tags=["Events"])

@router.post("/", response_model=EventOut, status_code=status.HTTP_201_CREATED)
async def create_event(event: EventCreate, db: AsyncSession = Depends(get_db)):
    return await create_event_service(db, event)

@router.get("/", response_model=PaginatedEvents)
async def list_events(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    timezone: str = Query('Asia/Kolkata', description="Timezone to display event times in")
):
    try:
        # Validate timezone
        pytz.timezone(timezone)
    except pytz.exceptions.UnknownTimeZoneError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid timezone: {timezone}"
        )
    
    events = await list_events_service(db, timezone)
    total = len(events)
    start = (page - 1) * size
    end = start + size
    events_out = [EventOut.from_orm(e) for e in events[start:end]]
    return PaginatedEvents(
        total=total,
        page=page,
        size=size,
        events=events_out
    )