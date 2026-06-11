import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

# Imports needed for setup
from app.main import app as fastapi_app
from app.database import get_session
from app.redis_client import redis_client
import app.main

@pytest.fixture(scope="session")
def client():
    # Apply global mocks before app starts
    redis_client.ping = AsyncMock(return_value=True)
    redis_client.aclose = AsyncMock()
    app.main.create_db_and_tables = AsyncMock()
    
    # Override database session
    async def override_get_session():
        yield MagicMock(spec=AsyncSession)
    
    fastapi_app.dependency_overrides[get_session] = override_get_session
    
    # Initialize TestClient
    with TestClient(fastapi_app) as c:
        # Manual state injection (lifespan simulation)
        c.app.state.httpx_client = AsyncMock()
        c.app.state.ai_client = AsyncMock()
        
        yield c
