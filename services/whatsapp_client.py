from app.config import settings 
import httpx

'''
post_webhook(), calls send_message() which is a synchronous method because we are using request library
This method is in charge of sending the whatsapp messages
I have to fix the responses of the events that my server is receiving that aren't messages
'''

async def send_message(phone_number : str, content: str, httpx_client: httpx.AsyncClient):
    meta_url = f"https://graph.facebook.com/v22.0/{settings.phone_number_id}/messages"

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
    return response