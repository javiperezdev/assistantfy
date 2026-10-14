from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.services.appointment.queries import get_appointments_for_day

router = APIRouter(tags=["Appointment"])

@router.get("/appointments")
async def get_appointments(business_id: int, date: date, session: AsyncSession = Depends(get_session)):
    appointments = await get_appointments_for_day(session=session, business_id=business_id, requested_date=date)
    if not appointments:
        return []
    return appointments
