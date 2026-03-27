from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.database import get_session
from app.services import client_service, service_service, appointment_service
from schemas.ai_tools import CheckAvailabilitySchema, BookAppointmentSchema
from datetime import timedelta

router = APIRouter()

'''
get_appointments it's a tool consumed by ai (that's why it's a post) 
it returns all the available spots to book an appointment
'''

@router.post("/get-availability")
def get_availability(requested_date: CheckAvailabilitySchema, session: Session = Depends(get_session)):
    return appointment_service.get_available_slots(session, requested_date)



@router.post("/book-appointment")
def book_appointment(phone_number: str, appointment_data: BookAppointmentSchema, session: Session = Depends(get_session)):
    client = client_service.search_client_by_phone_number(phone_number)
    if client is None:
        client = client_service.create_client(phone_number, appointment_data.client_name)
    
    service_name = appointment_data.service
    service_duration_minutes = service_service.get_time_from_service(service_name, session)
    end_time = appointment_data.start_time + timedelta(minutes=service_duration_minutes)

    return appointment_service.create_appointment(client.id, appointment_data.start_time, end_time)