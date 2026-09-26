from datetime import time
from sqlmodel import select
from app.models import BusinessHours
from sqlalchemy.ext.asyncio import AsyncSession


async def get_business_hours(business_id: int, session: AsyncSession):
    statement = select(BusinessHours).where(BusinessHours.business_id == business_id, BusinessHours.is_active == True)
    result = await session.exec(statement)
    return result.all()


async def create_business_hours(business_id: int, day_of_week: int, start_time: time, end_time: time, session: AsyncSession):
    hours = BusinessHours(business_id=business_id, day_of_week=day_of_week, start_time=start_time, end_time=end_time)
    session.add(hours)
    await session.commit()
    await session.refresh(hours)
    return hours


async def delete_business_hours(id: int, business_id: int, session: AsyncSession):
    statement = select(BusinessHours).where(BusinessHours.id == id, BusinessHours.business_id == business_id)
    result = await session.exec(statement)
    hours = result.first()
    if not hours:
        return None
    hours.is_active = False
    await session.commit()
    return hours


async def update_business_hours(id: int, business_id: int, day_of_week: int, start_time: time, end_time: time, session: AsyncSession):
    statement = select(BusinessHours).where(BusinessHours.id == id, BusinessHours.business_id == business_id)
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
