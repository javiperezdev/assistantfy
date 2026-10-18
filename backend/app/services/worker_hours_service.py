from datetime import time
from sqlmodel import select, update
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
        .where(WorkerHours.worker_id == worker_id, Worker.business_id == business_id, WorkerHours.is_active == True)
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


async def toggle_day(worker_id: int, business_id: int, day_of_week: int, is_active: bool, session: AsyncSession): 
    '''
    Method that toggles the is_active field of a worker's hours for a specific day of the week.
    If no record exists for the given day, it creates a new one with is_active set to True. 
    Returns None when the worker doesn't belong to that business, so callers can answer 404.
    '''
    # Tenant guard, same as create_worker_hours: without it, any business could
    # toggle another business's worker hours just by knowing the worker_id.
    worker = select(Worker).where(Worker.id == worker_id, Worker.business_id == business_id)
    if (await session.exec(worker)).first() is None:
        return None

    statement = (
        update(WorkerHours)
        .where(
            WorkerHours.worker_id == worker_id,
            WorkerHours.day_of_week == day_of_week,
        )
        .values(is_active=is_active)
    )

    result = await session.exec(statement)

    if not result.rowcount:  # No rows were updated, meaning no record exists for the given day
        # If no record exists for the given day, create a new one with is_active set to True (In the future we may create a method for this, but for now we will create it here)
        hour = WorkerHours(worker_id=worker_id, day_of_week=day_of_week, start_time=time(9, 0, 0), end_time=time(17, 0, 0), is_active=True)
        session.add(hour)
        await session.commit()
        await session.refresh(hour)
        return hour

    await session.commit()
    return result.rowcount




