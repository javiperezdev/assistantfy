from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.services.worker_service_service import get_worker_services, create_worker_service, delete_worker_service

router = APIRouter(tags=["Worker_service"])

@router.get("/worker-service")
async def get_worker_service_assignments(business_id: int, session: AsyncSession = Depends(get_session)):
    assignments = await get_worker_services(session=session, business_id=business_id)
    if not assignments:
        return []
    return assignments

@router.post("/worker-service", status_code=status.HTTP_201_CREATED)
async def assign_worker_to_service(service_id: int, business_id: int, worker_id: int, session: AsyncSession = Depends(get_session)):
    assignment = await create_worker_service(session=session, service_id=service_id, worker_id=worker_id, business_id=business_id)
    return assignment

@router.delete("/worker-service", status_code=status.HTTP_200_OK)
async def remove_worker_service_assignment(service_id: int, business_id: int, worker_id: int, session: AsyncSession = Depends(get_session)):
    await delete_worker_service(session=session, service_id=service_id, worker_id=worker_id, business_id=business_id)
    return {"service_id": service_id, "worker_id": worker_id}
