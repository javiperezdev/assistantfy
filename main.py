from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import uvicorn

app = FastAPI()

# This would be refactorized after MVP to core/config.py
class Settings(BaseSettings):
    verification_token: str
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
    messages: list[Message]

class Change(BaseModel):
    value: Value | None = None

class Entry(BaseModel):
    changes: list[Change]

class WebhookBody(BaseModel):
    entry: list[Entry]


'''
This is required for meta verification, I used an alias to access the 'hub.mode' 
and the two  'hub.', because we can't use directly that for the name of a variable,
I also use Query because arguments come from the url.
'''

@app.get("/webhook")
async def get_webhook(mode: str = Query(alias="hub.mode"), verify_token: str = Query(alias="hub.verify_token"), challenge: int = Query(alias="hub.challenge")):
    if mode == "subscribe":
        if verify_token == settings.verification_token:
            return challenge
    
    raise HTTPException(status_code=403, detail="Access is forbidden!")


@app.post("/webhook")
async def post_webhook(body: WebhookBody):
    message = body.entry[0].changes[0].value.messages[0]
    content = message.text.body
    phone_number = message.phone_number
    send_message(message)
    print(phone_number + " sent: " + content)
    return {"status": "ok"}

# Version might get us some trouble in the future, is something I have to study

'''
I need to implement request library to send whatsapp message
'''

@app.post(f"https://graph.facebook.com/v22.0/{settings.phone_number_id}/messages") 
async def send_message(message : Message, content: str):
    message_content = message.text.body
    return {"status" : "ok"}



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)