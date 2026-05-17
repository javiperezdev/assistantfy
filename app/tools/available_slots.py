from pydantic import BaseModel, Field, ValidationError
from datetime import date
from typing import Any
from sqlmodel import Session
from app.schemas.ai_tools import BaseTool, register_tool
from app.services.appointment_service import get_available_slots

class AvailableSlotsSchema(BaseModel):
    requested_date: date = Field(description="Fecha para la que el usuario pide cita en formato ISO 8601 (AAAA-MM-DD)")
    service_id: int = Field(description="ID númerico del servicio solicitado")

class GetAvailableSlotsTool(BaseTool):
    name: str = "get_available_slots"
    description: str = "Busca huecos libres para agendar una cita. Usala solo cuando te pregunten por disponibilidad o quieran agendar una cita."
    args_schema: type[BaseModel] = AvailableSlotsSchema

    async def run(self, context: Any, session: Session, **kwargs) -> Any:
        validated_args = self.args_schema(**kwargs)
            
        # Execution of business logic
        return await get_available_slots(
            session=session,
            business_id=context.business_id,
            service_id=validated_args.service_id,
            requested_date=validated_args.requested_date
        )

#Register tool when importing
register_tool(GetAvailableSlotsTool())
