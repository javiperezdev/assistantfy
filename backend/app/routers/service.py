from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession  
from app.services.service_service import get_all_services, create_service, delete_service
from app.database import get_session

router = APIRouter(tags=["Service"])

@router.get("/services")
async def get_services(business_id: int, session: AsyncSession = Depends(get_session)):
    services = await get_all_services(business_id=business_id, session=session)
    return services

@router.post("/service")
async def create_new_service(business_id: int, service_name: str, price: int, duration_minutes: int, session: AsyncSession = Depends(get_session)):
    service = await create_service(business_id=business_id, name=service_name, price=price, duration_minutes=duration_minutes, session=session)
    return service

@router.delete("/service", status_code=status.HTTP_200_OK)
async def remove_service(business_id: int, id: int, session: AsyncSession = Depends(get_session)):
    service = await delete_service(session=session, id=id, business_id=business_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"name": service.name}