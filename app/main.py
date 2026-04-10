from contextlib import asynccontextmanager
from fastapi import FastAPI
from .routers import whatsapp, clients, appointments
from .database import create_db_and_tables, engine
from openai import AsyncOpenAI
from .config import settings
import httpx
# I took the decision of importing models, to have them loaded when starting the server
from .models import Client, Service, Appointment, Business, BusinessHours, Worker, WorkerService, WorkerHours, AdminUser

@asynccontextmanager
async def lifespan(app: FastAPI): 
    httpx_client = httpx.AsyncClient()   
    ai_client = AsyncOpenAI(api_key=settings.deepseek_api_key, base_url="https://api.deepseek.com")
    await create_db_and_tables()
    yield {"httpx_client": httpx_client, "ai_client": ai_client}
    await httpx_client.aclose()
    await ai_client.close()
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
app.include_router(whatsapp.router)
app.include_router(clients.router)
app.include_router(appointments.router)

