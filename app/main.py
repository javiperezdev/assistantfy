from fastapi import FastAPI
from app.routers import whatsapp

app = FastAPI()
app.include_router(whatsapp.router)

@app.get("/")
async def root():
    return {"message" : "hello world!"}

