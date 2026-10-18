from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.services.appointment.queries import get_appointments_for_day
from app.services.appointment.commands import create_appointment_from_owner, set_appointment_state
from app.models import AppointmentState

router = APIRouter(tags=["Appointment"])

@router.get("/appointments")
async def get_appointments(business_id: int, date: date, session: AsyncSession = Depends(get_session)):
    appointments = await get_appointments_for_day(session=session, business_id=business_id, requested_date=date)
    if not appointments:
        return []
    return appointments

@router.post("/appointments", status_code=status.HTTP_201_CREATED)
async def add_appointment(business_id: int, phone_number: str, service_id: int, start_time: datetime,
                          name: str | None = None, worker_id: int | None = None,
                          session: AsyncSession = Depends(get_session)):
    result = await create_appointment_from_owner(
        session=session, business_id=business_id, phone_number=phone_number, name=name,
        service_id=service_id, worker_id=worker_id, start_time=start_time,
    )
    if result["status"] == "error":
        # Availability problems ("slot", "free") are conflicts, the rest are
        # bad requests (past time, unknown service/worker). Matching on our own
        # workflow messages instead of carrying an error code in every dict.
        # the workflow's `data` (alternative free slots) is dropped
        # here — upgrade path: put it in the 409 body if a form ever wants to
        # offer replacements.
        message = result["message"]
        is_conflict = "slot" in message.lower() or "free" in message.lower()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT if is_conflict else status.HTTP_400_BAD_REQUEST,
            detail=message,
        )
    return result

@router.patch("/appointment/state", status_code=status.HTTP_204_NO_CONTENT)
async def change_appointment_state(appointment_id: int, business_id: int, new_state: AppointmentState,
                                   session: AsyncSession = Depends(get_session)):
    rows_changed = await set_appointment_state(
        session=session, appointment_id=appointment_id, business_id=business_id, new_state=new_state,
    )
    if rows_changed == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found.")
