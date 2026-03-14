from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import whatsapp
import httpx

@asynccontextmanager
async def lifespan(app: FastAPI): 
    app.state.httpx_client = httpx.AsyncClient()   
    yield 
    await  app.state.httpx_client.aclose()

app = FastAPI(lifespan=lifespan)
app.include_router(whatsapp.router)

