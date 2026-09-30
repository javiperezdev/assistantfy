from datetime import time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.services.worker_hours_service import get_worker_hours, create_worker_hours, update_worker_hours, delete_worker_hour

router = APIRouter(tags=["WorkerHours"])

@router.get("/worker-hours")
async def get_worker_hours_slots(worker_id: int, business_id: int, session: AsyncSession = Depends(get_session)):
    hours = await get_worker_hours(worker_id=worker_id, business_id=business_id, session=session)
    if not hours:
        return []
    return hours

@router.post("/worker-hours", status_code=status.HTTP_201_CREATED)
async def add_worker_hour(worker_id: int, business_id: int, day_of_week: int, start_time: time, end_time: time, session: AsyncSession = Depends(get_session)):
    hour = await create_worker_hours(worker_id=worker_id, business_id=business_id, day_of_week=day_of_week, start_time=start_time, end_time=end_time, session=session)
    if hour is None:
        raise HTTPException(status_code=404, detail="Worker not found")
    return hour

@router.put("/worker-hours")
async def edit_worker_hour(id: int, worker_id: int, business_id: int, day_of_week: int, start_time: time, end_time: time, session: AsyncSession = Depends(get_session)):
    hour = await update_worker_hours(id=id, worker_id=worker_id, business_id=business_id, day_of_week=day_of_week, start_time=start_time, end_time=end_time, session=session)
    if hour is None:
        raise HTTPException(status_code=404, detail="Worker hour not found")
    return hour

@router.delete("/worker-hours", status_code=status.HTTP_200_OK)
async def remove_worker_hour(id: int, worker_id: int, business_id: int, session: AsyncSession = Depends(get_session)):
    hour = await delete_worker_hour(id=id, worker_id=worker_id, business_id=business_id, session=session)
    if hour is None:
        raise HTTPException(status_code=404, detail="Worker hour not found")
    return {"id": hour.id, "worker_id": hour.worker_id}
