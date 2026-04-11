from app.config import settings 
import httpx

'''
This method is triggered by generate_response from ai_service module.
It is in charge of sending the whatsapp messages.
'''

async def send_message(phone_number : str, content: str, httpx_client: httpx.AsyncClient):
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


    response = await httpx_client.post(url=meta_url, headers=meta_headers, json=payload)

    