from pydantic import BaseModel
from typing import Any
from sqlmodel import Session
from app.schemas.ai_tools import BaseTool, register_tool
from app.services.appointment.queries import get_client_appointments

class GetClientAppointmentsSchema(BaseModel):
    pass

class GetClientAppointmentsTool(BaseTool):
    name: str = "get_client_appointments"
    description: str = "Query the client's future appointments. Use it when the client asks about their appointments or wishes to cancel one."
    args_schema: type[BaseModel] = GetClientAppointmentsSchema

    async def run(self, context: Any, session: Session, **kwargs) -> Any:
        appointments = await get_client_appointments(session, context.client_phone_number)
        
        if not appointments:
            return {"status": "success", "message": "You have no booked appointments.", "data": []}
            
        return {
            "status": "success", 
            "message": "Client's future appointments:", 
            "data": [
                {"id": app.id, "start_time": app.start_time.isoformat(), "service_id": app.service_id} 
                for app in appointments
            ]
        }

register_tool(GetClientAppointmentsTool())
