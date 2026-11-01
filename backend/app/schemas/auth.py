from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=1024)


class AuthUser(BaseModel):
    id: int
    email: str
    business_id: int
    is_active: bool


class LoginResponse(BaseModel):
    user: AuthUser
    expires_in: int #seconds
    # Included when the client identifies itself as native (e.g. mobile app).
    access_token: str | None = None
