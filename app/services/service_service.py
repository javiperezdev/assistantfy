from app.schemas.ai_tools import ServiceType
from app.models import Service
from sqlmodel import Session, select

def get_time_from_service(name: ServiceType, session: Session):
    statement = select(Service.duration_minutes).where(Service.name == name)
    result = session.exec(statement)
    return result.first()