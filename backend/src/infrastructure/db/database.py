from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from main.config import Settings


class Base(DeclarativeBase):
    pass


async def get_session_stub() -> None:
    raise NotImplementedError


def create_async_session_maker(settings: Settings) -> async_sessionmaker:
    engine = create_async_engine(
        'postgresql+asyncpg://%s:%s@%s:5432/%s'
        % (
            settings.POSTGRES_USER,
            settings.POSTGRES_PASSWORD,
            settings.POSTGRES_HOST,
            settings.POSTGRES_DB,
        ),
    )
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_async_session(async_session_maker: async_sessionmaker) -> AsyncGenerator:
    async with async_session_maker() as session:
        yield session
