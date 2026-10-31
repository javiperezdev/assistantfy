import pytest
from sqlmodel import select

from app.models import AdminUser, Business
from app.scripts.create_admin import create_or_reset_admin, masked_url
from app.security import verify_password


def test_masked_url_hides_credentials():
    url = "postgresql+asyncpg://admin:secreto@db:5432/assistantfy_db"
    assert masked_url(url) == "postgresql+asyncpg://***@db:5432/assistantfy_db"
    assert "secreto" not in masked_url(url)


async def test_creates_business_and_admin(db_session):
    admin, action = await create_or_reset_admin(
        db_session,
        email="  Owner@Example.COM ",
        password="correct-horse-battery",
        business_name="Barbería Javi",
        business_phone="+34600111222",
    )

    assert action == "created"
    assert admin.email == "owner@example.com"
    assert verify_password("correct-horse-battery", admin.password_hash)

    business = await db_session.get(Business, admin.business_id)
    assert business.name == "Barbería Javi"


async def test_existing_email_resets_password_and_keeps_business(db_session):
    first, _ = await create_or_reset_admin(
        db_session,
        email="owner@example.com",
        password="correct-horse-battery",
        business_name="Barbería Javi",
        business_phone="+34600111222",
    )

    again, action = await create_or_reset_admin(
        db_session,
        email="owner@example.com",
        password="another-long-password",
        business_name="Otro negocio",
        business_phone="+34600999888",
    )

    assert action == "reset"
    assert again.id == first.id
    assert again.business_id == first.business_id
    assert verify_password("another-long-password", again.password_hash)
    assert not verify_password("correct-horse-battery", again.password_hash)

    businesses = (await db_session.exec(select(Business))).all()
    assert len(businesses) == 1


async def test_short_password_is_rejected(db_session):
    with pytest.raises(ValueError):
        await create_or_reset_admin(
            db_session,
            email="owner@example.com",
            password="corta",
            business_name="Barbería Javi",
            business_phone="+34600111222",
        )

    assert (await db_session.exec(select(AdminUser))).all() == []
