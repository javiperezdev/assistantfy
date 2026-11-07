"""Login rate limiting: 8 attempts per 15-minute window, per email+IP."""
import httpx
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import settings
from app.scripts.create_admin import create_or_reset_admin


async def _create_admin(session: AsyncSession):
    await create_or_reset_admin(
        session,
        email="owner@example.com",
        password="correct-horse-battery",
        business_name="Test Business",
        business_phone="+34600000000",
    )


def _attempt(auth_client: httpx.AsyncClient, email: str, password: str):
    return auth_client.post(
        "/API/auth/login",
        json={"email": email, "password": password},
    )


async def test_login_blocks_after_max_attempts(auth_client: httpx.AsyncClient, db_session: AsyncSession):
    await _create_admin(db_session)

    for _ in range(settings.login_max_attempts):
        response = await _attempt(auth_client, "owner@example.com", "wrong-password")
        assert response.status_code == 401

    response = await _attempt(auth_client, "owner@example.com", "wrong-password")
    assert response.status_code == 429
    assert int(response.headers["retry-after"]) > 0


async def test_successful_login_resets_counter(auth_client: httpx.AsyncClient, db_session: AsyncSession):
    await _create_admin(db_session)

    for _ in range(3):
        response = await _attempt(auth_client, "owner@example.com", "wrong-password")
        assert response.status_code == 401

    response = await _attempt(auth_client, "owner@example.com", "correct-horse-battery")
    assert response.status_code == 200

    # The counter was cleared: a full fresh window of failures is still allowed.
    for _ in range(settings.login_max_attempts):
        response = await _attempt(auth_client, "owner@example.com", "wrong-password")
        assert response.status_code == 401

    response = await _attempt(auth_client, "owner@example.com", "wrong-password")
    assert response.status_code == 429


async def test_rate_limit_is_scoped_by_email(auth_client: httpx.AsyncClient, db_session: AsyncSession):
    await _create_admin(db_session)

    for _ in range(settings.login_max_attempts):
        await _attempt(auth_client, "owner@example.com", "wrong-password")

    # A different email has its own counter and is not yet blocked.
    response = await _attempt(auth_client, "someone@else.com", "wrong-password")
    assert response.status_code == 401
