from pydantic import BaseModel, Field
from typing import Any
from sqlmodel import Session
from app.schemas.ai_tools import BaseTool, register_tool
from app.services.appointment.commands import cancel_appointment_workflow

class CancelAppointmentSchema(BaseModel):
    appointment_id: int = Field(description="ID de la cita a cancelar")

class CancelAppointmentTool(BaseTool):
    name: str = "cancel_appointment"
    description: str = "Cancela una cita específica del cliente. Úsala solo cuando el cliente haya confirmado qué cita desea cancelar."
    args_schema: type[BaseModel] = CancelAppointmentSchema

    async def run(self, context: Any, session: Session, **kwargs) -> Any:
        validated_args = self.args_schema(**kwargs)
        
        return await cancel_appointment_workflow(
            session=session,
            appointment_id=validated_args.appointment_id,
            client_phone_number=context.client_phone_number
        )

register_tool(CancelAppointmentTool())
