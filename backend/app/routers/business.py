from datetime import time
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.services.business_hours_service import get_business_hours, create_business_hours, update_business_hours, delete_business_hours

router = APIRouter(tags=["Business"])


@router.get("/business-hours")
async def get_hours(business_id: int, session: AsyncSession = Depends(get_session)):
    hours = await get_business_hours(business_id, session)
    return hours


@router.post("/business-hours", status_code=status.HTTP_201_CREATED)
async def add_hours(business_id: int, day_of_week: int, start_time: time, end_time: time, session: AsyncSession = Depends(get_session)):
    new_hours = await create_business_hours(business_id, day_of_week, start_time, end_time, session)
    return new_hours


@router.delete("/business-hours", status_code=status.HTTP_204_NO_CONTENT)
async def remove_hours(id: int, session: AsyncSession = Depends(get_session)):
    hours = await delete_business_hours(id, session)
    if not hours:
        raise HTTPException(status_code=404, detail="Business hours not found")


@router.put("/business-hours")
async def edit_hours(id: int, business_id: int, day_of_week: int, start_time: time, end_time: time, session: AsyncSession = Depends(get_session)):
    hours = await update_business_hours(id, business_id, day_of_week, start_time, end_time, session)
    if not hours:
        raise HTTPException(status_code=404, detail="Business hours not found")
    return hours
