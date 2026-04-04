from fastapi import APIRouter, Depends, Response
from sqlmodel import Session
from app.database import get_session
from app.services import client_service, service_service, appointment_service
from app.models import Appointment
from app.schemas.ai_tools import CheckAvailabilitySchema, BookAppointmentSchema
from datetime import date, datetime, timedelta

router = APIRouter(tags=["Appointments"])

'''
get_availability it's a tool consumed by ai that returns all the available spots 
to book an appointment on a requested_date
'''

@router.get("/get-availability")
async def get_availability(response: Response, requested_date: date, business_id: int, service_id: int, session: Session = Depends(get_session)):
    empty_slots = await appointment_service.get_available_slots(requested_date, session, business_id, service_id)
    if not empty_slots: 
        response.status_code = 404
        return {
            "status": "error",
                 "message": "There are no empty slots for the requested date, try with another date"
        }
    
    return {
        "status": "success",
        "data": empty_slots
    }



@router.post("/book-appointment")
async def book_appointment(response: Response, client_name: str, business_id: int, service_id: int, worker_id: int, phone_number: str, start_time: datetime, session: Session = Depends(get_session)):
    client = await client_service.search_client_by_phone_number(phone_number, session)
    if client is None:
        client = await client_service.create_client(business_id, client_name, phone_number, session)
    
    service_duration_minutes = await service_service.get_time_from_service(service_id, session)
    end_time = start_time + timedelta(minutes=service_duration_minutes)

    result = await appointment_service.create_appointment(business_id, client.id, service_id, worker_id, start_time, end_time, session)

    if type(result) != Appointment:  
        response.status_code = 404
        if result == []:
            return {
                "status": "error",
                "message": "El hueco solicitado acaba de ser ocupado y ya no quedan más citas libres para ese día. Dile al cliente que lo sientes y pregúntale si quiere buscar en otro día.",
                "data": []
            }
        
        return {
            "status": "error",
            "message": "Este hueco se ha acabado, ofrece las nuevas opciones en la variable 'data'",
            "data": result
        }

    response.status_code = 201
    return {
        "status": "success",
        "message": "La cita se ha guardado correctamente",
        "data": result
    }