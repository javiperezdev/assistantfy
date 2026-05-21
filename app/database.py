from sqlalchemy import text
from .config import settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

database_url = settings.database_url
engine = create_async_engine(database_url)


async def get_session():
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        # Create btree_gist extension and the exclusion constraint
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gist;"))
        await conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'exclude_overlapping_appointments') THEN
                    ALTER TABLE appointment 
                    ADD CONSTRAINT exclude_overlapping_appointments
                    EXCLUDE USING gist (
                        worker_id WITH =, 
                        tsrange(start_time, end_time) WITH &&
                    );
                END IF;
            END
            $$;
        """))