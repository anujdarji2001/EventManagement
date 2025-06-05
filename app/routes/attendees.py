from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import RegistrationCreate, RegistrationOut, PaginatedAttendees
from app.services import register_attendee_service, get_attendees_service

router = APIRouter(tags=["Attendees"])

@router.post("/events/{event_id}/register", response_model=RegistrationOut, status_code=status.HTTP_201_CREATED)
async def register_attendee(event_id: int, reg: RegistrationCreate, db: AsyncSession = Depends(get_db)):
    return await register_attendee_service(db, event_id, reg)

@router.get("/events/{event_id}/attendees", response_model=PaginatedAttendees)
async def list_attendees(
    event_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    return await get_attendees_service(db, event_id, page, size)
