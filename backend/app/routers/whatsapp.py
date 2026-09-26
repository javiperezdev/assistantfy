import logging
from fastapi import APIRouter, HTTPException, Query, Request, BackgroundTasks, Depends
from app.config import settings
from app.schemas.schemas_whatsapp import WebhookBody
from app.services.ai_service import generate_response, generate_system_prompt
from sqlalchemy.ext.asyncio import AsyncSession  
from app.database import get_session
from app.services.business_service import get_id_by_phone_number
from app.services.context_manager import get_context
from app.services.whatsapp_service import send_message

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Whatsapp"])

'''
Method required for meta verification, I used an alias to access the 'hub.mode' 
and the two  'hub.', because we can't use directly that for the name of a variable,
I also use Query because arguments come from the url.
'''

@router.get("/webhook")
async def get_webhook(mode: str = Query(alias="hub.mode"), verify_token: str = Query(alias="hub.verify_token"), challenge: int = Query(alias="hub.challenge")):
    if mode == "subscribe":
        if verify_token == settings.verification_token:
            return challenge
    
    raise HTTPException(status_code=403, detail="Access is forbidden!")

'''
Immediately returns 200 OK to prevent Meta webhook timeouts. 
The AI response is handled via a background_task, 
as the generation process exceeds Meta's mandatory response window.
'''

@router.post("/webhook")
async def post_webhook(body: WebhookBody, request: Request, background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    client_phone_number = None
    try:
        value = body.entry[0].changes[0].value
        business_phone_number = value.metadata.display_phone_number
        # While we don't implement a functionality to create a business, when it doesn't exist, we will maintain this log.
        logger.info(f"BUSINESS PHONE NUMBER: {business_phone_number}")
        business_id = await get_id_by_phone_number(session, business_phone_number)
        message = value.messages
        if message is not None:
            if message[0].text is None:
                logger.info("Incoming msg | business=%s client=%s content=%.100s", business_id, client_phone_number, "No text content")
                await send_message(client_phone_number, "You can only send text messages!", request.state.httpx_client)
                return {"status": "ok"} # Service won't allow non-text messages, so we return here to avoid further processing.
            content = message[0].text.body
            client_phone_number = message[0].phone_number

            logger.info("Incoming msg | business=%s client=%s content=%.100s", business_id, client_phone_number, content)

            # To avoid long messages, and possible attacks
            if len(content) > 160:
                error_message = "The message you have sent is too long, please try again with a shorter one!"
                await send_message(client_phone_number, error_message, request.state.httpx_client)
                return {"status": "ok"} # end execution 
                
            system_prompt = await generate_system_prompt(session, business_id)

            context = await get_context(client_phone_number, business_id)
            context.append({"role": "user", "content": content})
            logger.info("Offloading AI | client=%s", client_phone_number)
            background_tasks.add_task(generate_response, client_phone_number, context, request.state.httpx_client, request.state.ai_client, system_prompt, business_id, session)
        else: 
            logger.info("Status update | event=%s", value.statuses[0].get("status"))
    except Exception as e:
        logger.error("Webhook error | client=%s error=%s", client_phone_number, e, exc_info=True)
        if client_phone_number:
            error_message = "We're sorry, the service is not available at this moment."
            await send_message(client_phone_number, error_message, request.state.httpx_client)
    return {"status": "ok"}
