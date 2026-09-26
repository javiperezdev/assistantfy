from datetime import datetime, timedelta
from sqlmodel import select
from app.models import WorkerService, WorkerHours, Appointment, Worker
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

async def get_all_worker_hours(session: AsyncSession, worker_ids: list[int], day_of_week: int, business_id: int):
    '''
    Method that returns workers requested from a list containing their ids 
    for an specific day of the week, filtered by business
    '''
    statement = (
        select(WorkerHours)
        .join(Worker, WorkerHours.worker_id == Worker.id)
        .where(
            WorkerHours.worker_id.in_(worker_ids),
            WorkerHours.day_of_week == day_of_week,
            Worker.business_id == business_id,
            Worker.is_active == True
        )
    )
    result = await session.exec(statement)
    return result.all()

def group_by_workers(objects_list: list[WorkerHours] | list[Appointment]):
    """
    Groups all the appointment/workerHours by worker id (example: {1: ["10:00"], 2: ["11:00", "12:00"]})
    """
    workers_grouped = defaultdict(list)
    for object in objects_list:
        workers_grouped[object.worker_id].append(object)
        
    return workers_grouped

async def get_first_available_worker(session: AsyncSession, service_id: int, start_time: datetime, duration_minutes: int, business_id: int):
    """
    Returns the id from the worker who can perform the service
    """
    end_time = start_time + timedelta(minutes=duration_minutes)
    day_of_week = start_time.isoweekday()
    time_only = start_time.time()
    end_time_only = end_time.time()

    # Subquery to know if he has another appointment at the same time 
    overlapping_appointment = select(Appointment.id).where(
        Appointment.worker_id == WorkerService.worker_id,
        Appointment.start_time < end_time,
        Appointment.end_time > start_time
    )

    statement = (
        select(WorkerService.worker_id)
        .join(WorkerHours, WorkerService.worker_id == WorkerHours.worker_id)
        .join(Worker, WorkerService.worker_id == Worker.id)
        .where(Worker.business_id == business_id, Worker.is_active == True)
        .where(
            WorkerService.service_id == service_id,
            WorkerHours.day_of_week == day_of_week,
            WorkerHours.start_time <= time_only,
            WorkerHours.end_time >= end_time_only,
            ~overlapping_appointment.exists()  # ~ that symbol means NOT
        )
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
