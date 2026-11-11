import hashlib
import hmac
import logging
from fastapi import APIRouter, HTTPException, Query, Request, BackgroundTasks, Depends
from pydantic import ValidationError
from app.config import settings
from app.schemas.schemas_whatsapp import WebhookBody, Change, Message
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

def _has_valid_signature(raw_body: bytes, signature_header: str | None) -> bool:
    '''Meta signs the raw body with the app secret: "sha256=<hex digest>".'''
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = hmac.new(settings.meta_app_secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header.removeprefix("sha256="))

'''
Immediately returns 200 OK to prevent Meta webhook timeouts. 
The AI response is handled via a background_task, 
as the generation process exceeds Meta's mandatory response window.
'''

@router.post("/webhook")
async def post_webhook(request: Request, background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    # Verify Meta's HMAC before doing anything: the body is public input.
    raw_body = await request.body()
    if not _has_valid_signature(raw_body, request.headers.get("X-Hub-Signature-256")):
        logger.warning("Webhook rejected | invalid signature ip=%s", request.client.host if request.client else None)
        raise HTTPException(status_code=403, detail="Invalid signature")

    # Meta evolves the payload shape over time. Whatever we cannot parse is
    # logged and answered 200: a 4xx/5xx would make Meta retry a webhook we
    # can never act on.
    try:
        body = WebhookBody.model_validate_json(raw_body)
    except (ValidationError, ValueError) as e:
        logger.warning("Webhook ignored | unrecognised payload error=%s", e)
        return {"status": "ok"}

    for entry in body.entry:
        for change in entry.changes:
            await _process_change(change, request, background_tasks, session)

    return {"status": "ok"}


async def _process_change(change: Change, request: Request, background_tasks: BackgroundTasks, session: AsyncSession) -> None:
    # Only "messages" carries inbound chats. Everything else (account_update,
    # template status, quality update...) is config noise we acknowledge and drop.
    if change.field != "messages" or change.value is None:
        logger.info("Webhook ignored | field=%s", change.field)
        return

    value = change.value
    if value.metadata is None:
        # Delivery/read receipts: metadata present but no messages.
        logger.info("Status update | statuses=%s", value.statuses)
        return

    business_phone_number = value.metadata.display_phone_number
    try:
        business_id = await get_id_by_phone_number(session, business_phone_number)
    except Exception as e:
        logger.error("Webhook error | business lookup failed phone=%s error=%s", business_phone_number, e, exc_info=True)
        return
    if business_id is None:
        logger.warning("Webhook ignored | business not found phone=%s", business_phone_number)
        return

    messages = value.messages or []
    if not messages:
        logger.info("Status update | statuses=%s", value.statuses)
        return

    for message in messages:
        await _process_message(message, business_id, request, background_tasks, session)


async def _process_message(message: Message, business_id: int, request: Request, background_tasks: BackgroundTasks, session: AsyncSession) -> None:
    client_phone_number = message.phone_number
    try:
        if message.text is None:
            logger.info("Incoming msg | business=%s client=%s content=%s", business_id, client_phone_number, "No text content")
            # Service won't allow non-text messages, so we stop here.
            await send_message(client_phone_number, "You can only send text messages!", request.state.httpx_client)
            return

        content = message.text.body
        logger.info("Incoming msg | business=%s client=%s content=%.100s", business_id, client_phone_number, content)

        # To avoid long messages, and possible attacks
        if len(content) > 160:
            await send_message(client_phone_number, "The message you have sent is too long, please try again with a shorter one!", request.state.httpx_client)
            return

        system_prompt = await generate_system_prompt(session, business_id)
        context = await get_context(client_phone_number, business_id)
        context.append({"role": "user", "content": content})
        logger.info("Offloading AI | client=%s", client_phone_number)
        background_tasks.add_task(generate_response, client_phone_number, context, request.state.httpx_client, request.state.ai_client, system_prompt, business_id, session)
    except Exception as e:
        logger.error("Webhook error | client=%s error=%s", client_phone_number, e, exc_info=True)
        await send_message(client_phone_number, "We're sorry, the service is not available at this moment.", request.state.httpx_client)
