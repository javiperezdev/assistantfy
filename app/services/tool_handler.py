from pydantic import ValidationError
from sqlmodel import Session
from app.schemas.ai_tools import get_tool
from app.schemas.schemas_whatsapp import WhatsappContext
import app.tools  # Triggers __init__ which loads the tools
async def execute_tool(name: str, args: dict, context: WhatsappContext, session: Session):
    tool = get_tool(name)
    
    if not tool:
        return {"status": "error", "message": f"Tool {name} not found"}

    try:
        result = await tool.run(context=context, session=session, **args)
        return result

    # Catch the exception in case AI hallucinates or gave invalid args
    except ValidationError as e:
        return {
            "status": "error",
            "message": "Missing parameters or incorrect type.",
            "detalles": e.errors()
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": "Internal error executing the tool.",
            "detalles": str(e)
        }
