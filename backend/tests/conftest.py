import asyncio
from functools import partial
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from infrastructure.db.database import Base, get_session_stub
from main.config import get_settings
from main.main import app

settings = get_settings()

test_engine = create_async_engine(settings.test_db_uri, poolclass=NullPool)
Base.metadata.bind = test_engine


def create_test_async_session_maker(test_engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_test_async_session(test_async_session_maker: async_sessionmaker) -> AsyncGenerator:
    async with test_async_session_maker() as session:
        yield session


async_session_maker = create_test_async_session_maker(test_engine)

app.dependency_overrides[get_session_stub] = partial(
    get_test_async_session,
    async_session_maker,
)


@pytest.fixture(autouse=True, scope='module')
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='module')
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='module')
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test') as client:
        yield client


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
