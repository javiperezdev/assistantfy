from pydantic import ValidationError 
from sqlmodel import Session
from app.schemas.ai_tools import AvailableSlotsSchema
from app.schemas.schemas_whatsapp import WhatsappContext
from .appointment_service import get_available_slots

async def execute_tool(name: str, args: dict, context: WhatsappContext, session: Session):
    try:
        if name == "get_available_slots":
            requested_info = AvailableSlotsSchema(**args)
            
            result = await get_available_slots(
                requested_info=requested_info,
                session=session,
                business_id=context.business_id
            )
            return result

        return {"status": "error", "message": f"Tool {name} no encontrada"}


    # Correction to tell ai, that the types of quantity of arguments don't match with defined schema
    except ValidationError as e:
        return {
            "status": "error",
            "message": "Faltan parámetros o tienen el tipo incorrecto. Revisa el esquema de la función.",
            "detalles": e.errors() 
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": "Error interno en la base de datos",
            "detalles": str(e)
        }