from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any
from sqlmodel import Session, select
from app.models import Worker, WorkerService
from app.schemas.ai_tools import BaseTool, register_tool
from app.services.appointment_service import create_appointment, get_available_slots
from app.services.client_service import search_client_by_phone_number, create_client
from app.services.service_service import get_service_by_id
from datetime import timedelta

class BookAppointmentSchema(BaseModel):
    service_id: int = Field(description="ID númerico del servicio a reservar")
    worker_id: int = Field(description="ID del trabajador seleccionado")
    start_time: datetime = Field(description="Fecha y hora de inicio de la cita en formato ISO 8601 (AAAA-MM-DDTHH:MM:SS)")

class BookAppointmentTool(BaseTool):
    name: str = "book_appointment"
    description: str = "Reserva una cita con un trabajador y un servicio específicos. Úsala cuando el cliente haya confirmado la fecha, hora, trabajador y servicio."
    args_schema: type[BaseModel] = BookAppointmentSchema

    async def run(self, context: Any, session: Session, **kwargs) -> Any:
        validated_args = self.args_schema(**kwargs)
        
        # 1. Resolve client_id
        client = await search_client_by_phone_number(context.client_phone_number, session)
        if not client:
            # Create new client if phone number exists in context
            if context.client_phone_number:
                client = await create_client(
                    business_id=context.business_id,
                    name=None, # Name is optional
                    phone_number=context.client_phone_number,
                    session=session
                )
            else:
                return {"status": "error", "message": "No se pudo identificar al cliente por su número de teléfono."}
             
        # 2. Get service duration to calculate end_time
        service = await get_service_by_id(session, validated_args.service_id)
        if not service:
            return {"status": "error", "message": "El servicio no existe."}
            
        # 2.1 Verify business ownership and associations
        if service.business_id != context.business_id:
            return {"status": "error", "message": "El servicio no pertenece al negocio."}
        
        worker_statement = select(Worker).where(Worker.id == validated_args.worker_id)
        worker = (await session.exec(worker_statement)).first()
        if not worker:
            return {"status": "error", "message": "El trabajador no existe."}
            
        if worker.business_id != context.business_id:
            return {"status": "error", "message": "El trabajador no pertenece al negocio."}
            
        worker_service_statement = select(WorkerService).where(
            WorkerService.worker_id == validated_args.worker_id,
            WorkerService.service_id == validated_args.service_id
        )
        worker_service = (await session.exec(worker_service_statement)).first()
        if not worker_service:
            return {"status": "error", "message": "El trabajador no puede realizar este servicio."}

        end_time = validated_args.start_time + timedelta(minutes=service.duration_minutes)
        
        # 3. Create appointment
        return await create_appointment(
            business_id=context.business_id,
            client_id=client.id,
            service_id=validated_args.service_id,
            worker_id=validated_args.worker_id,
            start_time=validated_args.start_time,
            end_time=end_time,
            session=session
        )

# Register tool
register_tool(BookAppointmentTool())
