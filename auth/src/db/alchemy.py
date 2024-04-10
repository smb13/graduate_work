import typing

if typing.TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

engine: "AsyncEngine | None" = None  # type: ignore
async_session: sessionmaker | None = None

Base = declarative_base()
Base.__doc__ = "Базовый класс для моделей"


async def create_database() -> None:
    if engine:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


async def purge_database() -> None:
    if engine:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


async def get_session() -> typing.AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:  # type: ignore
        yield session
