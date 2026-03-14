from fastapi import APIRouter, HTTPException, Query, Request
from app.config import settings
from app.schemas import WebhookBody
from services.whatsapp_client import send_message

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
Method required for receiving messages from whatsapp, which triggers 'send_message()'
'''

@router.post("/webhook")
async def post_webhook(body: WebhookBody, request: Request):
    value = body.entry[0].changes[0].value
    message = value.messages
    if message is not None:
        content = message[0].text.body
        phone_number = message[0].phone_number
        await send_message(phone_number, content, request.app.state.httpx_client) # I need to configure BackGround tasks when implementing ai responses
    else:
        print(f"event: {value.statuses[0].get("status")}")
    return {"status": "ok"}
