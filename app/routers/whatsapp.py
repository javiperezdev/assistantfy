from fastapi import APIRouter, HTTPException, Query, Request, BackgroundTasks
from app.config import settings
from app.schemas.schemas_whatsapp import WebhookBody
from app.services.ai_service import generate_response

router = APIRouter()

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
async def post_webhook(body: WebhookBody, request: Request, background_tasks: BackgroundTasks):
    value = body.entry[0].changes[0].value
    message = value.messages
    if message is not None:
        content = message[0].text.body
        phone_number = message[0].phone_number
        background_tasks.add_task(generate_response, phone_number, content, request.state.httpx_client, request.state.ai_client) # I need to configure BackGround tasks when implementing ai responses
    else: 
        print(f"event: {value.statuses[0].get("status")}")
    return {"status": "ok"}
