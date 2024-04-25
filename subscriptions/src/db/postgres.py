import typing

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker

from models import Base

engine: AsyncEngine | None = None
async_session: sessionmaker | None = None


async def get_session() -> typing.AsyncGenerator[AsyncSession, None]:
    if not async_session:
        raise RuntimeError("Database is not initialized")

    async with async_session() as session:
        yield session


async def create_database() -> None:
    if not engine:
        raise RuntimeError("Database is not initialized")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def purge_database() -> None:
    if not engine:
        raise RuntimeError("Database is not initialized")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
