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
    requested_date: date = Field(description="Date for which the user is requesting an appointment in ISO 8601 format (YYYY-MM-DD)")
    service_id: int = Field(description="Numeric ID of the requested service")

class GetAvailableSlotsTool(BaseTool):
    name: str = "get_available_slots"
    description: str = "Find free slots to book an appointment. Use it only when asked about availability or when they want to book an appointment."
    args_schema: type[BaseModel] = AvailableSlotsSchema

    async def run(self, context: Any, session: Session, **kwargs) -> Any:
        validated_args = self.args_schema(**kwargs)
            
        business = await get_business_by_id(session, context.business_id)
        if not business:
            return {"status" : "error", "message" : "The entered ID is not attached to any business."}
        
        service = await get_service_by_id(session, validated_args.service_id)
        if not service:
            return {"status" : "error", "message" : "The service does not exist."}

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
