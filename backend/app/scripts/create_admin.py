"""Create a business and an admin account, or reset an admin's password.

Run it inside the API container: it needs the compose network and the .env.

    docker compose exec api python -m app.scripts.create_admin

Everything is prompted, so there is nothing to remember. The password is never
taken from the command line: it is typed (hidden) or read from ADMIN_PASSWORD
for automation. (This would be used in the MVP)
"""
import argparse
import asyncio
import getpass
import os

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import settings
from app.models import AdminUser, Business
from app.security import hash_password

MIN_PASSWORD_LENGTH = 12
DEFAULT_TIMEZONE = "Europe/Madrid"


def normalize_email(email: str) -> str:
    return email.strip().lower()


def masked_url(url: str) -> str:
    """Show which database we are about to write to, without leaking the password."""
    scheme, _, rest = url.partition("://")
    _, at, host = rest.rpartition("@")
    return f"{scheme}://***@{host}" if at else url


async def create_or_reset_admin(
    session: AsyncSession,
    *,
    email: str,
    password: str,
    business_id: int | None = None,
    business_name: str | None = None,
    business_phone: str | None = None,
    business_timezone: str = DEFAULT_TIMEZONE,
) -> tuple[AdminUser, str]:
    """Create the admin (and its business if needed) or reset its password.

    Returns the admin and what happened: "created" or "reset".
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"La contraseña necesita al menos {MIN_PASSWORD_LENGTH} caracteres.")

    email = normalize_email(email)
    admin = (await session.exec(select(AdminUser).where(AdminUser.email == email))).first()
    if admin is not None:
        # Usable as "I forgot my password". The business is left untouched.
        admin.password_hash = hash_password(password)
        admin.is_active = True
        await session.commit()
        await session.refresh(admin)
        return admin, "reset"

    business = await session.get(Business, business_id) if business_id else None
    if business is None:
        business = Business(
            name=business_name or "Assistantfy",
            phone_number=business_phone or "000000000",
            timezone=business_timezone,
        )
        session.add(business)
        await session.commit()
        await session.refresh(business)

    admin = AdminUser(
        business_id=business.id,
        email=email,
        password_hash=hash_password(password),
    )
    session.add(admin)
    await session.commit()
    await session.refresh(admin)
    return admin, "created"


def ask(label: str, default: str | None = None) -> str:
    hint = f" [{default}]" if default else ""
    value = input(f"  {label}{hint}: ").strip()
    return value or default or ""


def ask_password() -> str:
    while True:
        password = getpass.getpass("  Contraseña: ")
        if len(password) < MIN_PASSWORD_LENGTH:
            print(f"  ! mínimo {MIN_PASSWORD_LENGTH} caracteres")
        elif password != getpass.getpass("  Repite:     "):
            print("  ! no coinciden")
        else:
            return password


async def ask_business(session: AsyncSession, business_id: int | None) -> dict:
    if business_id:
        return {"business_id": business_id}

    businesses = (await session.exec(select(Business))).all()
    if businesses:
        print("  Negocios existentes:")
        for business in businesses:
            print(f"    {business.id} - {business.name}")

    chosen = ask("ID del negocio (vacío = crear uno nuevo)")
    if chosen:
        if not chosen.isdigit():
            raise ValueError("El ID del negocio debe ser un número.")
        return {"business_id": int(chosen)}

    print("  Nuevo negocio:")
    return {
        "business_name": ask("Nombre", "Assistantfy"),
        "business_phone": ask("Teléfono", "ej: +34665789098"),
        "business_timezone": ask("Zona horaria", DEFAULT_TIMEZONE),
    }


async def run(args: argparse.Namespace) -> None:
    print()
    print(f"  BD destino: {masked_url(settings.database_url)}")
    print()

    engine = create_async_engine(settings.database_url)
    try:
        async with AsyncSession(engine, expire_on_commit=False) as session:
            email = normalize_email(args.email or ask("Email"))
            existing = (
                await session.exec(select(AdminUser).where(AdminUser.email == email))
            ).first()
            password = os.environ.get("ADMIN_PASSWORD") or ask_password()

            if existing is not None:
                print(
                    f"  ! Ya existe un admin con ese email "
                    f"(id={existing.id}, business_id={existing.business_id})."
                )
                if input("  ¿Resetear su contraseña? [s/N]: ").strip().lower() not in (
                    "s",
                    "si",
                    "sí",
                    "y",
                    "yes",
                ):
                    print("  Cancelado. No se ha tocado nada.")
                    return
                admin, action = await create_or_reset_admin(
                    session, email=email, password=password
                )
            else:
                business = await ask_business(session, args.business_id)
                admin, action = await create_or_reset_admin(
                    session, email=email, password=password, **business
                )

            if action == "created":
                print(
                    f"  ✓ Admin creado: {admin.email} "
                    f"(id={admin.id}, business_id={admin.business_id})"
                )
            else:
                print(f"  ✓ Contraseña actualizada: {admin.email} (id={admin.id})")
    finally:
        await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Crear un negocio + admin, o resetear la contraseña de un admin."
    )
    parser.add_argument("--email", help="Si se omite, se pregunta.")
    parser.add_argument(
        "--business-id", type=int, help="Negocio existente al que enganchar el admin."
    )
    args = parser.parse_args()

    try:
        asyncio.run(run(args))
    except (KeyboardInterrupt, EOFError):
        print("\n  Cancelado.")
        raise SystemExit(1)
    except ValueError as exc:
        print(f"\n  ! {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
