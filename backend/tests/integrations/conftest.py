import time as time_module
from unittest.mock import AsyncMock

import httpx
import pytest
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings
from app.database import get_session
from app.main import app as fastapi_app
from app.models import *

from sqlalchemy import text


class FakeRedis:
    """In-memory Redis substitute with TTL support for auth tests."""

    def __init__(self):
        self._data: dict[str, tuple[str, float]] = {}

    async def get(self, key: str) -> str | None:
        if key not in self._data:
            return None
        value, expires_at = self._data[key]
        if expires_at and time_module.time() > expires_at:
            del self._data[key]
            return None
        return value

    async def set(self, key: str, value: str, *, ex: int) -> None:
        self._data[key] = (value, time_module.time() + ex)

    async def delete(self, key: str) -> None:
        self._data.pop(key, None)

    async def ping(self) -> bool:
        return True

    async def aclose(self) -> None:
        pass

@pytest.fixture(scope="function", autouse=True)
async def create_tables():
    engine = create_async_engine(settings.test_database_url)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
        # Create btree_gist extension and the exclusion constraint
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gist;"))
        await conn.execute(text("""
            ALTER TABLE appointment ADD CONSTRAINT exclude_overlapping_appointments
            EXCLUDE USING GIST (
                worker_id WITH =,
                tsrange(start_time, end_time) WITH &&
            );
        """))
    yield
    await engine.dispose()

@pytest.fixture
async def db_session():
    test_engine = create_async_engine(settings.test_database_url)
    TestingSessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()
        await test_engine.dispose()

@pytest.fixture
async def auth_client(db_session: AsyncSession, monkeypatch):
    """An httpx client bound to the real app, with Redis faked and the DB
    session overridden. The client's cookie jar persists across requests.
    """
    fake = FakeRedis()
    monkeypatch.setattr("app.main.redis_client", fake)
    monkeypatch.setattr("app.services.auth_service.redis_client", fake)
    # The lifespan must not hit the dev DB (configured via .env); tables are
    # already created by the integration conftest.
    monkeypatch.setattr("app.main.create_db_and_tables", AsyncMock())

    async def override_get_session():
        yield db_session

    fastapi_app.dependency_overrides[get_session] = override_get_session

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=fastapi_app),
        base_url="http://testserver",
    ) as client:
        yield client

    fastapi_app.dependency_overrides.clear()


@pytest.fixture
async def two_businesses(db_session):
    # Two tenants, ready to use: tests checking that queries never cross the
    # tenant boundary unpack this instead of seeding their own businesses.
    business_a = Business(phone_number="311", name="Business A", timezone="UTC")
    business_b = Business(phone_number="322", name="Business B", timezone="UTC")
    db_session.add_all([business_a, business_b])
    await db_session.commit()
    await db_session.refresh(business_a)
    await db_session.refresh(business_b)
    return business_a, business_b
