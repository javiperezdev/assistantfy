from app.config import settings 
import requests # I will replace it with 'httpx' (asynchronous)

'''
post_webhook(), calls send_message() which is a synchronous method because we are using request library
This method is in charge of sending the whatsapp messages
I have to fix the responses of the events that my server is receiving that aren't messages
'''

def send_message(phone_number : str, content: str):
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

    response = requests.post(url=meta_url, headers=meta_headers, json=payload)