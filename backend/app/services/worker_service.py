from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
from sqlmodel import func, select
from app.models import AppointmentState, Business, WorkerService, WorkerHours, Appointment, Worker
from collections import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession

async def get_workers_by_service(session: AsyncSession, service_id: int, business_id: int):
    '''
    Method that returns workers able to perform a requested service
    '''
    statement = (
        select(WorkerService.worker_id)
        .join(Worker, WorkerService.worker_id == Worker.id)
        .where(WorkerService.service_id == service_id, Worker.business_id == business_id, Worker.is_active == True)
    )
    result = (await session.exec(statement)).all()
    return result

def group_by_workers(objects_list: list[WorkerHours] | list[Appointment]):
    """
    Groups all the appointment/workerHours by worker id (example: {1: ["10:00"], 2: ["11:00", "12:00"]})
    """
    workers_grouped = defaultdict(list)
    for object in objects_list:
        workers_grouped[object.worker_id].append(object)
        
    return workers_grouped

async def get_first_available_worker(
    session: AsyncSession,
    service_id: int,
    start_time: datetime,
    duration_minutes: int,
    business_id: int,
) -> int | None:
    """
    Return the available worker with the fewest upcoming booked
    appointments. Return None if no worker is available.
    """
    # Load the business timezone.
    business = await session.get(Business, business_id)
    if business is None:
        raise ValueError("Business not found")

    business_tz = ZoneInfo(business.timezone)

    # Appointments are stored as naive business-local timestamps (same as
    # queries.py/calculator.py), and Appointment.start_time is TIMESTAMP WITHOUT
    # TIME ZONE: binding an aware datetime there makes asyncpg fail. A naive
    # input already means business-local time (see validate_appointment_creation).
    if start_time.tzinfo is None or start_time.utcoffset() is None:
        start_time = start_time.replace(tzinfo=business_tz)

    # Calculate the requested appointment interval.
    end_time = start_time + timedelta(minutes=duration_minutes)

    # Working hours are defined in the business's local timezone.
    local_start = start_time.astimezone(business_tz)
    local_end = end_time.astimezone(business_tz)

    # pspans crossing local midnight are compared against the start day
    # only, so no WorkerHours row can cover them -> returns None. Split the query
    # over both days if overnight shifts ever become a thing.
    day_of_week = local_start.isoweekday()
    naive_start = local_start.replace(tzinfo=None)
    naive_end = local_end.replace(tzinfo=None)
    start_time_only = naive_start.time()
    end_time_only = naive_end.time()

    # Find appointments that conflict with the requested interval.
    overlapping_appointment = (
        select(Appointment.id)
        .where(
            Appointment.business_id == business_id,
            Appointment.worker_id == WorkerService.worker_id,
            Appointment.appointment_state == AppointmentState.BOOKED,
            Appointment.start_time < naive_end,
            Appointment.end_time > naive_start,
        )
        .correlate(WorkerService)
    )

    # Count each candidate worker's future booked appointments.
    upcoming_appointments = (
        select(func.count(Appointment.id))
        .where(
            Appointment.business_id == business_id,
            Appointment.worker_id == WorkerService.worker_id,
            Appointment.appointment_state == AppointmentState.BOOKED,
            Appointment.start_time >= naive_start,
        )
        .correlate(WorkerService)
        .scalar_subquery()
    )

    # Filter eligible workers and choose the least busy one.
    statement = (
        select(WorkerService.worker_id)
        .join(
            Worker,
            (Worker.id == WorkerService.worker_id)
            & (Worker.business_id == WorkerService.business_id),
        )
        .join(
            WorkerHours,
            WorkerHours.worker_id == Worker.id,
        )
        .where(
            WorkerService.business_id == business_id,
            WorkerService.service_id == service_id,
            Worker.is_active.is_(True),
            WorkerHours.is_active.is_(True),
            WorkerHours.day_of_week == day_of_week,
            WorkerHours.start_time <= start_time_only,
            WorkerHours.end_time >= end_time_only,
            ~overlapping_appointment.exists(),
        )
        .order_by(upcoming_appointments.asc())
        .limit(1)
    )

    result = await session.exec(statement)
    return result.first()


async def get_all_workers(business_id: int, session: AsyncSession):
    statement = select(Worker).where(Worker.business_id == business_id, Worker.is_active == True)
    result = await session.exec(statement)
    return result.all()

async def add_worker(business_id: int, name: str, session: AsyncSession):
    new_worker = Worker(business_id=business_id, name=name)
    session.add(new_worker)
    await session.commit()
    await session.refresh(new_worker) # Refresh to have the new data with automatic id.
    return new_worker

async def delete_worker(business_id: int, id: int, session: AsyncSession):
    statement = select(Worker).where(Worker.business_id == business_id, Worker.id == id)
    worker = await session.exec(statement)
    worker = worker.first()
    if worker is None:
        return None
    worker.is_active = False
    await session.commit()
    return worker
