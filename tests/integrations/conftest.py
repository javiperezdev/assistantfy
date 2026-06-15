import pytest
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings
from app.models import *

from sqlalchemy import text

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
