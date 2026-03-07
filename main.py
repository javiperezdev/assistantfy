from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
import uvicorn

app = FastAPI()

# This would be refactorized after MVP to core/config.py
class Settings(BaseSettings):
    whatsapp_token: str
    model_config = SettingsConfigDict(env_file=".env")

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

# Meta verification webhook (this would be refactorized after the mvp)

@app.post("/webhook")
async def


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)