from sqlmodel import select, delete
from sqlalchemy import func
from app.models import Worker, WorkerService
from sqlalchemy.ext.asyncio import AsyncSession

async def get_worker_services(session: AsyncSession, business_id: int):
    statement = (
        select(WorkerService.service_id,
        func.array_agg(WorkerService.worker_id).label("worker_ids"))
        .join(Worker, WorkerService.worker_id == Worker.id)
        .where(WorkerService.business_id == business_id, Worker.is_active == True)
        .group_by(WorkerService.service_id)
    )
    result = await session.exec(statement)
    rows = result.all()
    return dict(rows) 


async def create_worker_service(session: AsyncSession, business_id: int, service_id: int, worker_id: int):
    assignment = WorkerService(service_id=service_id, worker_id=worker_id, business_id=business_id)
    session.add(assignment)
    await session.commit()
    return assignment

async def delete_worker_service(session: AsyncSession, business_id: int, service_id: int, worker_id: int):
    statement = delete(WorkerService).where(
        WorkerService.service_id == service_id,
        WorkerService.worker_id == worker_id,
        WorkerService.business_id==business_id
    )
    await session.exec(statement)
    await session.commit()
