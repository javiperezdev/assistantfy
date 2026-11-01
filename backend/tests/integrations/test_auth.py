import time
from unittest.mock import AsyncMock

import httpx
import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import settings
from app.database import get_session
from app.main import app as fastapi_app
from app.scripts.create_admin import create_or_reset_admin


class FakeRedis:
    """In-memory Redis substitute with TTL support for auth tests."""

    def __init__(self):
        self._data: dict[str, tuple[str, float]] = {}

    async def get(self, key: str) -> str | None:
        if key not in self._data:
            return None
        value, expires_at = self._data[key]
        if expires_at and time.time() > expires_at:
            del self._data[key]
            return None
        return value

    async def set(self, key: str, value: str, *, ex: int) -> None:
        self._data[key] = (value, time.time() + ex)

    async def delete(self, key: str) -> None:
        self._data.pop(key, None)

    async def ping(self) -> bool:
        return True

    async def aclose(self) -> None:
        pass


@pytest.fixture
async def auth_client(db_session: AsyncSession, monkeypatch):
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


async def _create_admin(session: AsyncSession, email: str, password: str):
    admin, _ = await create_or_reset_admin(
        session,
        email=email,
        password=password,
        business_name="Test Business",
        business_phone="+34600000000",
    )
    return admin


async def test_login_success(auth_client: httpx.AsyncClient, db_session: AsyncSession):
    await _create_admin(db_session, "owner@example.com", "correct-horse-battery")

    response = await auth_client.post(
        "/API/auth/login",
        json={"email": "owner@example.com", "password": "correct-horse-battery"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == "owner@example.com"
    assert data["user"]["business_id"] is not None
    assert data["expires_in"] == settings.session_ttl_seconds
    assert data.get("access_token") is None
    assert "assistantfy_session=" in response.headers["set-cookie"]


async def test_login_native_returns_access_token(auth_client: httpx.AsyncClient, db_session: AsyncSession):
    await _create_admin(db_session, "owner@example.com", "correct-horse-battery")

    response = await auth_client.post(
        "/API/auth/login",
        json={"email": "owner@example.com", "password": "correct-horse-battery"},
        headers={"X-Client": "native"},
    )

    assert response.status_code == 200
    assert response.json()["access_token"] is not None


async def test_login_wrong_password(auth_client: httpx.AsyncClient, db_session: AsyncSession):
    await _create_admin(db_session, "owner@example.com", "correct-horse-battery")

    response = await auth_client.post(
        "/API/auth/login",
        json={"email": "owner@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert "set-cookie" not in response.headers


async def test_login_missing_email(auth_client: httpx.AsyncClient):
    response = await auth_client.post(
        "/API/auth/login",
        json={"email": "noone@example.com", "password": "any-long-password"},
    )

    assert response.status_code == 401


async def test_me_authenticated(auth_client: httpx.AsyncClient, db_session: AsyncSession):
    await _create_admin(db_session, "owner@example.com", "correct-horse-battery")
    await auth_client.post(
        "/API/auth/login",
        json={"email": "owner@example.com", "password": "correct-horse-battery"},
    )

    response = await auth_client.get("/API/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == "owner@example.com"


async def test_me_unauthenticated(auth_client: httpx.AsyncClient):
    response = await auth_client.get("/API/auth/me")

    assert response.status_code == 401


async def test_logout(auth_client: httpx.AsyncClient, db_session: AsyncSession):
    await _create_admin(db_session, "owner@example.com", "correct-horse-battery")
    await auth_client.post(
        "/API/auth/login",
        json={"email": "owner@example.com", "password": "correct-horse-battery"},
    )

    response = await auth_client.post("/API/auth/logout")
    assert response.status_code == 204

    response = await auth_client.get("/API/auth/me")
    assert response.status_code == 401


async def test_me_with_bearer_token(auth_client: httpx.AsyncClient, db_session: AsyncSession):
    await _create_admin(db_session, "owner@example.com", "correct-horse-battery")
    login_response = await auth_client.post(
        "/API/auth/login",
        json={"email": "owner@example.com", "password": "correct-horse-battery"},
        headers={"X-Client": "native"},
    )
    token = login_response.json()["access_token"]

    auth_client.cookies.clear()
    response = await auth_client.get("/API/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == "owner@example.com"
