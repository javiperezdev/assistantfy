from pydantic import ValidationError 
from sqlmodel import Session
from app.schemas.ai_tools import AvailableSlotsAiSchema
from app.schemas.schemas_whatsapp import WhatsappContext
from .appointment_service import get_next_available_slots_for_ai

async def execute_tool(name: str, args: dict, context: WhatsappContext, session: Session):
    try:
        if name == "get_next_available_slots_for_ai":
            requested_info = AvailableSlotsAiSchema(**args, business_id=context.business_id)
            
            result = await get_next_available_slots_for_ai(
                requested_info=requested_info,
                session=session
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