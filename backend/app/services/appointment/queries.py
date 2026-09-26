from sqlmodel import select
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo
from app.models import Appointment, AppointmentState, Client
from app.services.worker_service import get_all_worker_hours, group_by_workers
from app.services.business_service import get_business_by_id
from app.services.appointment.calculator import subtract_sets, hide_past_slots
from sqlalchemy.ext.asyncio import AsyncSession

async def get_client_appointments(session: AsyncSession, client_phone_number: str, business_id: int):
    """
    Get all the future appointments from a client
    """
    # Appointment times are stored in the business timezone as naive datetimes,
    # so "now" must be computed in that same timezone to compare correctly.
    business = await get_business_by_id(session, business_id)
    now = datetime.now(ZoneInfo(business.timezone)).replace(tzinfo=None) if business else datetime.now()

    statement = (
        select(Appointment)
        .join(Client)
        .where(Appointment.business_id == business_id)
        .where(Client.business_id == business_id)
        .where(Client.phone_number == client_phone_number)
        .where(Appointment.start_time >= now)
    )
    result = await session.exec(statement)
    return result.all()

async def get_all_appointments(session: AsyncSession, workers_id: list[int], requested_date: date, business_id: int):
    start_of_day = datetime.combine(requested_date, time.min)
    end_of_day = datetime.combine(requested_date, time.max)
    statement = (
        select(Appointment)
        .where(Appointment.business_id == business_id)
        .where(Appointment.worker_id.in_(workers_id))
        .where(Appointment.appointment_state == AppointmentState.BOOKED)
        .where(Appointment.start_time >= start_of_day, Appointment.end_time <= end_of_day)
    )
    result = (await session.exec(statement)).all()
    return result
    
async def get_available_slots(session: AsyncSession, business_id: int, worker_ids: list[int], duration: timedelta, requested_date: date, timezone: ZoneInfo):
    all_hours = await get_all_worker_hours(session, worker_ids, requested_date.isoweekday(), business_id)
    all_appointments = await get_all_appointments(session, worker_ids, requested_date, business_id)

    hours_by_worker = group_by_workers(all_hours)
    apps_by_worker = group_by_workers(all_appointments)

    total_available_slots = set()

    for worker_id in worker_ids:
        worker_hours = hours_by_worker.get(worker_id, [])
        worker_apps = apps_by_worker.get(worker_id, [])
        
        slots_libres = subtract_sets(worker_hours, worker_apps, duration, requested_date)
        total_available_slots.update(slots_libres)     

    result = sorted(list(total_available_slots))
    return hide_past_slots(result, requested_date, timezone)
