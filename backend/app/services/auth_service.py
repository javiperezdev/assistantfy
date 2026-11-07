"""Session-based authentication helpers.

Nothing outside this module should touch Redis session keys directly, so the
key format and TTL live in one place.
"""
import secrets
from typing import Annotated

from fastapi import Depends, Cookie, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.config import settings
from app.database import get_session
from app.models import AdminUser
from app.redis_client import redis_client
from app.security import hash_password, new_session_token, token_key, verify_password


_DUMMY_HASH: str | None = None


def _get_dummy_hash() -> str:
    """Return an Argon2 hash that is never valid, used for timing-safe failures."""
    global _DUMMY_HASH
    if _DUMMY_HASH is None:
        # Lazy: first failed login pays the Argon2 cost once, not on import.
        _DUMMY_HASH = hash_password(secrets.token_urlsafe(32))
    return _DUMMY_HASH


def _session_key(token: str) -> str:
    return f"sess:{token_key(token)}"


def _rate_limit_key(email: str, ip: str) -> str:
    """Redis key for the login attempt counter, one bucket per email+IP."""
    return f"rate:login:{email.strip().lower()}:{ip}"


async def check_login_rate_limit(email: str, ip: str) -> int | None:
    """Count a login attempt; return Retry-After seconds when rate-limited.

    Runs *before* any Argon2 work: hashing is the expensive step an attacker
    wants to trigger, so this counter is what protects it. The window is fixed
    (the key expires ``login_rate_window_seconds`` after the *first* attempt,
    not on every attempt) so a slow trickle can't keep sliding the window open.
    """
    key = _rate_limit_key(email, ip)
    attempts = await redis_client.incr(key)
    if attempts == 1:
        await redis_client.expire(key, settings.login_rate_window_seconds)
    if attempts > settings.login_max_attempts:
        ttl = await redis_client.ttl(key)
        return ttl if ttl > 0 else settings.login_rate_window_seconds
    return None


async def reset_login_rate_limit(email: str, ip: str) -> None:
    """Clear the attempt counter after a successful login."""
    await redis_client.delete(_rate_limit_key(email, ip))


async def authenticate(session: AsyncSession, email: str, password: str) -> AdminUser | None:
    """Verify email + password and return the admin, or None on any failure.

    Always executes Argon2 once, even when the email does not exist, so callers
    cannot distinguish missing users from wrong passwords by response time.
    """
    normalized_email = email.strip().lower()
    admin = (
        await session.exec(select(AdminUser).where(AdminUser.email == normalized_email))
    ).first()

    if admin is None or not admin.is_active:
        # Burn the same CPU/memory so the timing is indistinguishable.
        verify_password(password, _get_dummy_hash())
        return None

    if not verify_password(password, admin.password_hash):
        return None

    return admin


async def create_session(admin_id: int) -> str:
    """Create a new opaque session and return the raw token."""
    token = new_session_token()
    await redis_client.set(
        _session_key(token),
        str(admin_id),
        ex=settings.session_ttl_seconds,
    )
    return token


async def read_session(token: str) -> int | None:
    """Resolve a raw token to an admin id, or None if missing/expired."""
    admin_id = await redis_client.get(_session_key(token))
    if admin_id is None:
        return None
    return int(admin_id)


async def delete_session(token: str) -> None:
    """Revoke a session immediately."""
    await redis_client.delete(_session_key(token))


def _pick_token(
    cookie_token: str | None,
    bearer: HTTPAuthorizationCredentials | None,
) -> str | None:
    """Return the token from the cookie or the Authorization header."""
    if cookie_token:
        return cookie_token
    if bearer:
        return bearer.credentials
    return None


async def get_current_admin(
    session: AsyncSession = Depends(get_session),
    cookie_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
    bearer: Annotated[HTTPAuthorizationCredentials | None, Security(HTTPBearer(auto_error=False))] = None,
) -> AdminUser | None:
    """FastAPI dependency that returns the current admin or None."""
    token = _pick_token(cookie_token, bearer)
    if token is None:
        return None

    admin_id = await read_session(token)
    if admin_id is None:
        return None

    admin = await session.get(AdminUser, admin_id)
    if admin is None or not admin.is_active:
        return None

    return admin


async def require_current_admin(
    admin: AdminUser = Depends(get_current_admin),
) -> AdminUser:
    """FastAPI dependency that returns the admin or raises 401."""
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    return admin


async def require_business_id(
    admin: AdminUser = Depends(require_current_admin),
) -> int:
    """FastAPI dependency that returns the session's business id.

    Replaces the client-supplied ``business_id`` query parameter: the tenant is
    derived from the authenticated admin, never taken from the request.
    """
    return admin.business_id


async def get_optional_token(
    cookie_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
    bearer: Annotated[HTTPAuthorizationCredentials | None, Security(HTTPBearer(auto_error=False))] = None,
) -> str | None:
    """FastAPI dependency used by logout: token is optional."""
    return _pick_token(cookie_token, bearer)
