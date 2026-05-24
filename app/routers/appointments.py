from fastapi import APIRouter, Depends, Response
from sqlmodel import Session
from app.database import get_session
from app.services import client_service, service_service
from app.services.appointment.queries import get_available_slots
from app.services.appointment.commands import create_appointment_workflow
from app.services.worker_service import get_workers_by_service
from app.services.business_service import get_business_by_id
from app.services.service_service import get_service_by_id
from zoneinfo import ZoneInfo
from datetime import date, datetime, timedelta

router = APIRouter(tags=["Appointments"])

'''
Not using router for the current phase
'''

@router.post("/get-availability")
async def get_availability(response: Response, requested_date: date, service_id: int, business_id: int, session: Session = Depends(get_session)):
    business = await get_business_by_id(session, business_id)
    if not business:
        response.status_code = 404
        return {"status": "error", "message": "Negocio no encontrado"}
    
    service = await get_service_by_id(session, service_id)
    if not service:
        response.status_code = 404
        return {"status": "error", "message": "Servicio no encontrado"}

    worker_ids = await get_workers_by_service(session, service_id)
    
    empty_slots = await get_available_slots(
        session, 
        worker_ids, 
        timedelta(minutes=service.duration_minutes), 
        requested_date, 
        ZoneInfo(business.timezone)
    )
    
    # Adapt result to match old structure for backward compatibility if needed, 
    # but the tool now returns the list directly.
    if not empty_slots:
        response.status_code = 404
        return {"status": "error", "message": "No hay huecos disponibles"}

    response.status_code = 200
    return {"status": "success", "data": empty_slots}

@router.post("/book-appointment")
async def book_appointment(response: Response, client_name: str, business_id: int, service_id: int, worker_id: int, phone_number: str, start_time: datetime, session: Session = Depends(get_session)):
    client = await client_service.search_client_by_phone_number(phone_number, session)
    if client is None:
        client = await client_service.create_client(business_id, client_name, phone_number, session)
    
    result = await create_appointment_workflow(
        session=session,
        business_id=business_id,
        client_id=client.id,
        service_id=service_id,
        worker_id=worker_id,
        start_time=start_time
    )

    if result["status"] == "error":  
        response.status_code = 404
        return result
            
    response.status_code = 201
    return result
   