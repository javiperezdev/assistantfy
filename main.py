from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import uvicorn
import requests

app = FastAPI()

# This would be refactorized after MVP to core/config.py
class Settings(BaseSettings):
    verification_token: str
    whatsapp_token: str
    phone_number_id: str
    # I have declared extra=ignore just for testing reasons, I should change this before the MVP
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

# Message is receiving only content now because we are doing a CRUD, this should change

temporal_messages : dict[int, str] = {}

@app.get("/")
async def root():
    return {"message" : "hello world!"}

@app.get("/messages/")
async def receive_message():
    return temporal_messages

@app.get("/messages/{id}")
async def search_message(id: int):
    if id not in temporal_messages:
        raise HTTPException(status_code=404, detail=f"There isn't a message with id: {id}")
    return temporal_messages[id]

# whatsapp webhook (this would be refactorized after the mvp)

class Text(BaseModel):
    body: str

# 'text' attribute accepts None because there are some cases, where we won't receive text (audio, img...) 

class Message(BaseModel):
    phone_number: str = Field(alias="from")
    text: Text | None = None

class Value(BaseModel):
    messages: list[Message] | None = None # It can be none, to avoid status calls
    statuses: list[dict] | None = None

class Change(BaseModel):
    value: Value | None = None

class Entry(BaseModel):
    changes: list[Change]

class WebhookBody(BaseModel):
    entry: list[Entry]


'''
Method required for meta verification, I used an alias to access the 'hub.mode' 
and the two  'hub.', because we can't use directly that for the name of a variable,
I also use Query because arguments come from the url.
'''

@app.get("/webhook")
async def get_webhook(mode: str = Query(alias="hub.mode"), verify_token: str = Query(alias="hub.verify_token"), challenge: int = Query(alias="hub.challenge")):
    if mode == "subscribe":
        if verify_token == settings.verification_token:
            return challenge
    
    raise HTTPException(status_code=403, detail="Access is forbidden!")

'''
Method required for receiving messages from whatsapp, which triggers 'send_message()'
'''

@app.post("/webhook")
async def post_webhook(body: WebhookBody):
    value = body.entry[0].changes[0].value
    message = value.messages
    if message is not None:
        content = message[0].text.body
        phone_number = message[0].phone_number
        send_message(phone_number, content)
    else:
        print(f"event: {value.statuses[0].get("status")}")
    return {"status": "ok"}


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


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)