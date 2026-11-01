from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_session
from app.models import AdminUser
from app.schemas.auth import AuthUser, LoginRequest, LoginResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    response: Response,
    session: AsyncSession = Depends(get_session),
    x_client: str | None = Header(None),
):
    admin = await auth_service.authenticate(session, payload.email, payload.password)
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = await auth_service.create_session(admin.id)

    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        httponly=True,
        samesite="lax",
        secure=settings.session_cookie_secure,
        path=settings.session_path,
        max_age=settings.session_max_age_seconds,
    )

    native_mode = x_client is not None and x_client.lower() == "native"
    return LoginResponse(
        user=AuthUser(
            id=admin.id,
            email=admin.email,
            business_id=admin.business_id,
            is_active=admin.is_active,
        ),
        expires_in=settings.session_ttl_seconds,
        access_token=token if native_mode else None,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    token: str | None = Depends(auth_service.get_optional_token),
):
    if token:
        await auth_service.delete_session(token)

    response.delete_cookie(
        key=settings.session_cookie_name,
        path=settings.session_path,
    )


@router.get("/me", response_model=AuthUser)
async def me(admin: AdminUser = Depends(auth_service.require_current_admin)):
    return AuthUser(
        id=admin.id,
        email=admin.email,
        business_id=admin.business_id,
        is_active=admin.is_active,
    )
