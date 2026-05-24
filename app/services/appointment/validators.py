from sqlmodel import select, Session
from datetime import datetime
from zoneinfo import ZoneInfo
from app.models import Worker, WorkerService
from app.services.service_service import get_service_by_id
from app.services.business_service import get_business_by_id

async def validate_appointment_creation(session: Session, business_id: int, service_id: int, worker_id: int, start_time: datetime):
    # 0. Validate time
    business = await get_business_by_id(session, business_id)
    if not business:
        return {"status": "error", "message": "El negocio no existe."}
    
    tz = ZoneInfo(business.timezone)
    # Ensure start_time is timezone-aware
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=tz)
        
    if start_time < datetime.now(tz):
        return {"status": "error", "message": "No puedes reservar una cita en el pasado."}

    # 1. Validate Service
    service = await get_service_by_id(session, service_id)
    if not service:
        return {"status": "error", "message": "El servicio no existe."}
    
    if service.business_id != business_id:
        return {"status": "error", "message": "El servicio no pertenece al negocio."}

    # 2. Validate Worker
    worker_statement = select(Worker).where(Worker.id == worker_id)
    worker = (await session.exec(worker_statement)).first()
    if not worker:
        return {"status": "error", "message": "El trabajador no existe."}
        
    if worker.business_id != business_id:
        return {"status": "error", "message": "El trabajador no pertenece al negocio."}

    # 3. Validate Worker-Service Association
    worker_service_statement = select(WorkerService).where(
        WorkerService.worker_id == worker_id,
        WorkerService.service_id == service_id
    )
    worker_service = (await session.exec(worker_service_statement)).first()
    if not worker_service:
        return {"status": "error", "message": "El trabajador no puede realizar este servicio."}

    return {"status": "success", "service": service}
