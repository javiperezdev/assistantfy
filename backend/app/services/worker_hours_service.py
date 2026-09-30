from datetime import time
from sqlmodel import select
from app.models import Worker, WorkerHours
from sqlalchemy.ext.asyncio import AsyncSession

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

async def get_worker_hours(worker_id: int, business_id: int, session: AsyncSession):
    '''
    Method that returns every hour slot of a worker, filtered by business
    '''
    statement = (
        select(WorkerHours)
        .join(Worker, WorkerHours.worker_id == Worker.id)
        .where(WorkerHours.worker_id == worker_id, Worker.business_id == business_id)
        .order_by(WorkerHours.day_of_week, WorkerHours.start_time)
    )
    result = await session.exec(statement)
    return result.all()

async def create_worker_hours(worker_id: int, business_id: int, day_of_week: int, start_time: time, end_time: time, session: AsyncSession):
    '''
    Method that creates an hour slot for a worker of the given business.
    Returns None when the worker doesn't belong to that business, so callers can answer 404.
    '''
    worker = select(Worker).where(Worker.id == worker_id, Worker.business_id == business_id)
    if (await session.exec(worker)).first() is None:
        return None
    hours = WorkerHours(worker_id=worker_id, day_of_week=day_of_week, start_time=start_time, end_time=end_time)
    session.add(hours)
    await session.commit()
    await session.refresh(hours)
    return hours

async def update_worker_hours(id: int, worker_id: int, business_id: int, day_of_week: int, start_time: time, end_time: time, session: AsyncSession):
    '''
    Method that updates one hour slot, only if it belongs to the given worker and business.
    Returns None when it doesn't match, so callers can answer 404.
    '''
    statement = (
        select(WorkerHours)
        .join(Worker, WorkerHours.worker_id == Worker.id)
        .where(
            WorkerHours.id == id,
            WorkerHours.worker_id == worker_id,
            Worker.business_id == business_id
        )
    )
    result = await session.exec(statement)
    hours = result.first()
    if not hours:
        return None
    hours.day_of_week = day_of_week
    hours.start_time = start_time
    hours.end_time = end_time
    await session.commit()
    await session.refresh(hours)
    return hours

async def delete_worker_hour(id: int, worker_id: int, business_id: int, session: AsyncSession):
    '''
    Method that hard-deletes one hour slot, only if it belongs to the given worker and business.
    Returns None when it doesn't match, so callers can answer 404.
    '''
    statement = (
        select(WorkerHours)
        .join(Worker, WorkerHours.worker_id == Worker.id)
        .where(
            WorkerHours.id == id,
            WorkerHours.worker_id == worker_id,
            Worker.business_id == business_id
        )
    )
    result = await session.exec(statement)
    hour = result.first()
    if hour is None:
        return None
    # Hard delete: nothing else filters WorkerHours.is_active, so a soft-deleted
    # row would still block slots in the appointment availability queries.
    await session.delete(hour)
    await session.commit()
    return hour
