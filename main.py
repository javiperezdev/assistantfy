from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
import uvicorn

app = FastAPI()

# This would be refactorized after MVP to core/config.py
class Settings(BaseSettings):
    verification_token: str
    # I have declared extra=ignore just for testing reasons, I should change this before the MVP
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

# Message is receiving only content now because we are doing a CRUD, this should change

class Message(BaseModel):
    content: str

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

# Id is generated this way because we are doing a CRUD, this should change

@app.post("/messages/") 
async def send_message(message : Message):
    temporal_messages[len(temporal_messages)] = message.content
    return {"message" : message.content}

# whatsapp webhook (this would be refactorized after the mvp)

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
async def post_webhook(body: dict):
    print(body)
    return {"status": "ok"}



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)