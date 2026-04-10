from fastapi import APIRouter, HTTPException, Query, Request, BackgroundTasks, Depends
from app.config import settings
from app.schemas.schemas_whatsapp import WebhookBody
from app.services.ai_service import generate_response, generate_system_prompt
from sqlmodel import Session
from app.database import get_session
from app.services.business_service import get_id_by_phone_number

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
async def post_webhook(body: WebhookBody, request: Request, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    value = body.entry[0].changes[0].value
    business_phone_number = value.metadata.display_phone_number
    business_id = await get_id_by_phone_number(session, business_phone_number)
    message = value.messages
    if message is not None:
        content = message[0].text.body
        print(f"mensaje de whatsapp: {content}")
        system_prompt = await generate_system_prompt(session, business_id)
        client_phone_number = message[0].phone_number
        background_tasks.add_task(generate_response, client_phone_number, content, request.state.httpx_client, request.state.ai_client, system_prompt, business_id, session)
    else: 
        print(f"event: {value.statuses[0].get("status")}")
    return {"status": "ok"}
