from urllib.parse import quote_plus
from .config import settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

secret_password = quote_plus(settings.postgres_password)
database_url = f"postgresql+asyncpg://{settings.postgres_user}:{secret_password}@localhost:5432/{settings.postgres_db}"
# Echo true has to be removed
engine = create_async_engine(database_url, echo=True)


async def get_session():
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)