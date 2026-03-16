from contextlib import asynccontextmanager
from fastapi import FastAPI
from .routers import whatsapp
from .config import settings
from openai import AsyncOpenAI
import httpx


@asynccontextmanager
async def lifespan(app: FastAPI): 
    httpx_client = httpx.AsyncClient()   
    ai_client = AsyncOpenAI(api_key=settings.deepseek_api_key, base_url="https://api.deepseek.com")
    yield {"httpx_client": httpx_client, "ai_client": ai_client}
    await httpx_client.aclose()
    await ai_client.close()

app = FastAPI(lifespan=lifespan)
app.include_router(whatsapp.router)

