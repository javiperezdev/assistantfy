import logging
from app.config import settings 
import httpx

logger = logging.getLogger(__name__)

async def send_message(phone_number : str, content: str, httpx_client: httpx.AsyncClient):
    '''
    Method in charge of sending a message to a phone number
    '''
    meta_url = f"https://graph.facebook.com/v25.0/{settings.phone_number_id}/messages"

    # meta is strict so the keys should have this name 

    meta_headers = {
        "Authorization": f"Bearer {settings.whatsapp_token}",
        "Content-Type": "application/json"
    }

    # Currently, our method is just forwarding what the user is sending 

    payload = {
    "messaging_product": "whatsapp",
    "to": phone_number,
    "type": "text",
    "text": {"body": content}
    }

    try:
        response = await httpx_client.post(url=meta_url, headers=meta_headers, json=payload)
        response.raise_for_status()
        resp_json = response.json()
        msg_id = resp_json.get("messages", [{}])[0].get("id")
        logger.info("WhatsApp sent | to=%s status=%s msg_id=%s content=%.100s",
                    phone_number, response.status_code, msg_id, content)
    except Exception as e:
        # Meta explains the real failure in the response body (expired token 190,
        # code 100/subcode 33 when the token can't access the phone number id...).
        # raise_for_status() alone only says "400 Bad Request", so log the body too.
        body = getattr(getattr(e, "response", None), "text", "")
        logger.error("WhatsApp send failed | to=%s error=%s body=%.300s", phone_number, e, body)
        raise

    