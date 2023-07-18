import asyncio
import os
from typing import AsyncGenerator

import pytest
from dotenv import load_dotenv
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from db.database import Base, get_async_session
from main import app

load_dotenv()

POSTGRES_USER_TEST = os.getenv('POSTGRES_USER_TEST')
POSTGRES_PASSWORD_TEST = os.getenv('POSTGRES_PASSWORD_TEST')
POSTGRES_HOST_TEST = os.getenv('POSTGRES_HOST_TEST')
POSTGRES_DB_TEST = os.getenv('POSTGRES_DB_TEST')

DATABASE_URL_TEST = (
    f'postgresql+asyncpg://{POSTGRES_USER_TEST}:{POSTGRES_PASSWORD_TEST}@'
    f'{POSTGRES_HOST_TEST}:5432/{POSTGRES_DB_TEST}'
)

engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_maker = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)
Base.metadata.bind = engine_test


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(autouse=True, scope='module')
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
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
