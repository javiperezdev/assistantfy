from fastapi import APIRouter, Depends, Response
from sqlmodel import Session
from app.database import get_session
from app.services import client_service, service_service, appointment_service
from datetime import datetime, timedelta
from app.schemas.ai_tools import AvailableSlotsAiSchema

router = APIRouter(tags=["Appointments"])

'''
Not using router for the current phase
'''

@router.post("/get-availability")
async def get_availability(response: Response, requested_info: AvailableSlotsAiSchema, session: Session = Depends(get_session)):
    empty_slots = await appointment_service.get_next_available_slots_for_ai(requested_info, session)
    if empty_slots["status"] == "success":
        response.status_code = 200
        return empty_slots

    response.status_code = 404
    return empty_slots

@router.post("/book-appointment")
async def book_appointment(response: Response, client_name: str, business_id: int, service_id: int, worker_id: int, phone_number: str, start_time: datetime, session: Session = Depends(get_session)):
    client = await client_service.search_client_by_phone_number(phone_number, session)
    if client is None:
        client = await client_service.create_client(business_id, client_name, phone_number, session)
    
    service_duration_minutes = await service_service.get_time_from_service(service_id, session)
    end_time = start_time + timedelta(minutes=service_duration_minutes)

    result = await appointment_service.create_appointment(business_id, client.id, service_id, worker_id, start_time, end_time, session)

    if result["status"] == "error":  
        response.status_code = 404
        return result
            
    response.status_code = 201
    return result
   