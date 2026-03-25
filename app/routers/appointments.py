from fastapi import APIRouter, Depends
from sqlmodel import Session
from database import get_session
from services import appointment_service
from schemas.ai_tools import CheckAvailabilitySchema

router = APIRouter()

@router.get("/availability")
def get_appointments(requested_date: CheckAvailabilitySchema, session: Session = Depends(get_session)):
    return appointment_service.get_available_slots(session, requested_date)