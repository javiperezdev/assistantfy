from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel
from .routers import whatsapp
from .config import settings
from .database import engine
from openai import AsyncOpenAI
import httpx
# I took the decission of importing models, to have them loaded when starting the server
from .models import Client, Service, Appointment, ServiceAppointment 


@asynccontextmanager
async def lifespan(app: FastAPI): 
    httpx_client = httpx.AsyncClient()   
    ai_client = AsyncOpenAI(api_key=settings.deepseek_api_key, base_url="https://api.deepseek.com")
    SQLModel.metadata.create_all(engine)
    yield {"httpx_client": httpx_client, "ai_client": ai_client}
    await httpx_client.aclose()
    await ai_client.close()
    engine.dispose()

app = FastAPI(lifespan=lifespan)
app.include_router(whatsapp.router)

