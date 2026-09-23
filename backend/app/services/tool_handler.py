import json
import logging
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession 
from app.schemas.ai_tools import get_tool
from app.schemas.schemas_whatsapp import WhatsappContext
import app.tools  # Triggers __init__ which loads the tools

logger = logging.getLogger(__name__)

async def execute_tool(name: str, args: dict, context: WhatsappContext, session: AsyncSession):
    logger.info("Tool execute | name=%s args=%.200s", name, json.dumps(args))

    tool = get_tool(name)
    
    if not tool:
        logger.warning("Tool not found | name=%s", name)
        return {"status": "error", "message": f"Tool {name} not found"}

    try:
        result = await tool.run(context=context, session=session, **args)
        logger.info("Tool ok | name=%s", name)
        return result

    # Catch the exception in case AI hallucinates or gave invalid args
    except ValidationError as e:
        logger.warning("Tool validation error | name=%s errors=%s", name, e.errors())
        return {
            "status": "error",
            "message": "Missing parameters or incorrect type.",
            "detalles": e.errors()
        }
    
    except Exception as e:
        logger.error("Tool error | name=%s error=%s", name, e, exc_info=True)
        return {
            "status": "error",
            "message": "Internal error executing the tool.",
            "detalles": str(e)
        }
