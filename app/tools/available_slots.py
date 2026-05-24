from pydantic import BaseModel, Field, ValidationError
from datetime import date
from typing import Any
from sqlmodel import Session
from app.schemas.ai_tools import BaseTool, register_tool
from app.services.appointment.queries import get_available_slots
from app.services.service_service import get_service_by_id
from app.services.business_service import get_business_by_id
from app.services.worker_service import get_workers_by_service
from zoneinfo import ZoneInfo
from datetime import timedelta

class AvailableSlotsSchema(BaseModel):
    requested_date: date = Field(description="Fecha para la que el usuario pide cita en formato ISO 8601 (AAAA-MM-DD)")
    service_id: int = Field(description="ID númerico del servicio solicitado")

class GetAvailableSlotsTool(BaseTool):
    name: str = "get_available_slots"
    description: str = "Busca huecos libres para agendar una cita. Usala solo cuando te pregunten por disponibilidad o quieran agendar una cita."
    args_schema: type[BaseModel] = AvailableSlotsSchema

    async def run(self, context: Any, session: Session, **kwargs) -> Any:
        validated_args = self.args_schema(**kwargs)
            
        business = await get_business_by_id(session, context.business_id)
        if not business:
            return {"status" : "error", "message" : "El id introducido no esta adherido a ningún negocio."}
        
        service = await get_service_by_id(session, validated_args.service_id)
        if not service:
            return {"status" : "error", "message" : "El servicio no existe."}

        worker_ids = await get_workers_by_service(session, validated_args.service_id)
        
        return await get_available_slots(
            session=session,
            worker_ids=worker_ids,
            duration=timedelta(minutes=service.duration_minutes),
            requested_date=validated_args.requested_date,
            timezone=ZoneInfo(business.timezone)
        )

#Register tool when importing
register_tool(GetAvailableSlotsTool())
