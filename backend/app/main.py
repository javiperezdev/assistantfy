import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import whatsapp, worker, worker_service, service, business, appointment
from .database import create_db_and_tables, engine
from openai import AsyncOpenAI
from .config import settings
from .redis_client import redis_client
import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", stream=sys.stdout)
# I took the decision of importing models, to have them loaded when starting the server
from .models import Client, Service, Appointment, Business, BusinessHours, Worker, WorkerService, WorkerHours, AdminUser

@asynccontextmanager
async def lifespan(app: FastAPI): 
    """
    This method "turns on" the database, OpenAI, httpx and redis client when the server is launched,
    on the other hand before shut down, server "closes the conection" with all this clients.
    """
    httpx_client = httpx.AsyncClient()   
    ai_client = AsyncOpenAI(api_key=settings.ai_api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
    await redis_client.ping()
    await create_db_and_tables()
    yield {"httpx_client": httpx_client, "ai_client": ai_client}
    await httpx_client.aclose()
    await ai_client.close()
    await redis_client.aclose()
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
app.include_router(whatsapp.router)
app.include_router(worker.router, prefix="/API")
app.include_router(worker_service.router, prefix="/API")
app.include_router(service.router, prefix="/API")
app.include_router(business.router, prefix="/API")
app.include_router(appointment.router, prefix="/API")

origins = [
    settings.front_end_url
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

