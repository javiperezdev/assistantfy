from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from app.models import Appointment
from app.services.appointment.validators import validate_appointment_creation
from app.services.appointment.queries import get_available_slots
from app.services.business_service import get_business_by_id
from app.services.worker_service import get_workers_by_service, get_first_available_worker
from zoneinfo import ZoneInfo
from app.services.client_service import search_client_by_phone_number, create_client
from app.services.service_service import get_time_from_service
from sqlalchemy.ext.asyncio import AsyncSession

async def cancel_appointment_workflow(session: AsyncSession, appointment_id: int, client_phone_number: str, business_id: int):
    client = await search_client_by_phone_number(client_phone_number, business_id, session)
    if not client:
        return {"status": "error", "message": "Client not found."}

    # Check appointments
    appointment_statement = select(Appointment).where(
        Appointment.id == appointment_id,
        Appointment.business_id == business_id
    )
    appointment = (await session.exec(appointment_statement)).first()
    if not appointment:
        return {"status": "error", "message": "Appointment not found."}

    # If another client tries to cancel the appointment, we should not allow it
    if appointment.client_id != client.id:
        return {"status": "error", "message": "This appointment does not belong to you or you do not have permission to cancel it."}

    try:
        await session.delete(appointment)
        await session.commit()
        return {"status": "success", "message": "Appointment successfully cancelled."}
    except Exception:
        await session.rollback()
        return {"status": "error", "message": "Error cancelling the appointment."}

# DON'T CHANGE THE COMMENTS UNTIL APPOINTMENT.PY HAS A SOLUTION (currently relying on what messages are displaying) 

async def create_appointment_workflow(session: AsyncSession, business_id: int, client_id: int, service_id: int, worker_id: int, start_time: datetime):
    # 1. Validation
    val_res = await validate_appointment_creation(session, business_id, service_id, worker_id, start_time)
    if val_res["status"] == "error":
        return val_res
    
    service = val_res["service"]
    end_time = start_time + timedelta(minutes=service.duration_minutes)

    # 2. Check availability
    appointment = Appointment(business_id=business_id, client_id=client_id, service_id=service_id, worker_id=worker_id, start_time=start_time, end_time=end_time)
    slot_exists = (await (session.exec(
        select(Appointment).where(
            Appointment.business_id == business_id,
            Appointment.worker_id == worker_id,
            Appointment.start_time < end_time,
            Appointment.end_time > start_time                               
    )))).first()

    if slot_exists:
        # Re-fetch slots for error response
        business = await get_business_by_id(session, business_id)
        worker_ids = await get_workers_by_service(session, service_id, business_id)
        tz = ZoneInfo(business.timezone)
        
        new_slots = await get_available_slots(session, business_id, worker_ids, timedelta(minutes=service.duration_minutes), start_time.date(), tz)
        
        if not new_slots:
             return {
                "status": "error",
                "message": "The requested slot has just been taken and there are no more free appointments for that day.",
                "data": []
            }

        return {
            "status": "error",
            "message": "This slot is no longer available, offer the new options in the 'data' variable",
            "data": new_slots
        }

    # 3. Create
    try:
        session.add(appointment)
        await session.commit()
        await session.refresh(appointment)
        return {
            "status": "success",
            "message": "The appointment has been saved successfully",
            "data": []
        }
    except IntegrityError:
        await session.rollback()
        # Handle race condition
        return {"status": "error", "message": "Error saving, the slot was taken."}

async def create_appointment_from_owner(session: AsyncSession, business_id: int, phone_number: str, name: str | None, service_id: int, worker_id: int | None, start_time: datetime):
    """
    Booking from the web app (the owner typing in a form), as opposed to the
    WhatsApp flow which goes through the AI tool. Composes the same pieces:
    resolve-or-create client, pick a free worker if none was chosen, then the
    shared workflow does validation/overlap/race handling.
    """
    # Resolve client: same phone-based lookup the AI tool uses
    client = await search_client_by_phone_number(phone_number, business_id, session)
    if not client:
        client = await create_client(business_id=business_id, name=name, phone_number=phone_number, session=session)

    # No worker chosen -> first free worker for that service/slot (same helper as the AI)
    if worker_id is None:
        duration_minutes = await get_time_from_service(service_id, business_id, session)
        if duration_minutes is None:
            return {"status": "error", "message": "The service does not exist."}
        worker_id = await get_first_available_worker(session, service_id, start_time, duration_minutes, business_id)
        if worker_id is None:
            return {"status": "error", "message": "No worker is free for this service at the requested time."}

    return await create_appointment_workflow(
        session=session,
        business_id=business_id,
        client_id=client.id,
        service_id=service_id,
        worker_id=worker_id,
        start_time=start_time,
    )
