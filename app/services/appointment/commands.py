from sqlmodel import select, Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from app.models import Appointment
from app.services.appointment.validators import validate_appointment_creation
from app.services.appointment.queries import get_available_slots
from app.services.business_service import get_business_by_id
from app.services.worker_service import get_workers_by_service
from zoneinfo import ZoneInfo
from app.services.client_service import search_client_by_phone_number

async def cancel_appointment_workflow(session: Session, appointment_id: int, client_phone_number: str):
    client = await search_client_by_phone_number(client_phone_number, session)
    if not client:
        return {"status": "error", "message": "Client not found."}

    # Check appointments
    appointment = await session.get(Appointment, appointment_id)
    if not appointment:
        return {"status": "error", "message": "Appointment not found."}

    # Safety check 
    if appointment.client_id != client.id:
        return {"status": "error", "message": "This appointment does not belong to you or you do not have permission to cancel it."}

    try:
        await session.delete(appointment)
        await session.commit()
        return {"status": "success", "message": "Appointment successfully cancelled."}
    except Exception:
        await session.rollback()
        return {"status": "error", "message": "Error cancelling the appointment."}
async def create_appointment_workflow(session: Session, business_id: int, client_id: int, service_id: int, worker_id: int, start_time: datetime):
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
        worker_ids = await get_workers_by_service(session, service_id)
        tz = ZoneInfo(business.timezone)
        
        new_slots = await get_available_slots(session, worker_ids, timedelta(minutes=service.duration_minutes), start_time.date(), tz)
        
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
