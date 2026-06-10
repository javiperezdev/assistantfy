import pytest
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings

@pytest.fixture
async def db_session():
    test_engine = create_async_engine(settings.test_database_url)
    TestingSessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async with TestingSessionLocal() as session:
        await session.begin()
        yield session
        await session.rollback()
        await test_engine.dispose() 