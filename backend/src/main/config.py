import os
from pathlib import Path

from celery import Celery
from pydantic import BaseSettings


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_DB: str

    POSTGRES_USER_TEST: str
    POSTGRES_PASSWORD_TEST: str
    POSTGRES_HOST_TEST: str
    POSTGRES_DB_TEST: str

    JWT_ACCESS_SECRET_KEY: str = 'JWT'
    JWT_REFRESH_SECRET_KEY: str = 'JWT'
    SECRET_TOKEN_FOR_EMAIL: str = 'JWT'
    ALGORITHM: str = 'HS256'

    EMAIl_HOST: str
    EMAIL_HOST_PASSWORD: str

    REDIS_HOST: str = 'localhost'

    ROOT_DIR = '%s' % Path(__file__).parent.parent
    MEDIA_ROOT = 'media/images'

    @property
    def db_uri(self) -> str:
        return 'postgresql+asyncpg://%s:%s@%s:5432/%s' % (
            self.POSTGRES_USER,
            self.POSTGRES_PASSWORD,
            self.POSTGRES_HOST,
            self.POSTGRES_DB,
        )

    @property
    def test_db_uri(self) -> str:
        return 'postgresql+asyncpg://%s:%s@%s:5432/%s' % (
            self.POSTGRES_USER_TEST,
            self.POSTGRES_PASSWORD_TEST,
            self.POSTGRES_HOST_TEST,
            self.POSTGRES_DB_TEST,
        )

    class Config:
        env_file = '.env', '../.env'


def get_settings() -> Settings:
    return Settings()


celery_app = Celery(
    'blog',
    broker=f'redis://{get_settings().REDIS_HOST}:6379/0',
)
celery_app.autodiscover_tasks(
    [f'domain.tasks.{module}' for module in os.listdir(f'{get_settings().ROOT_DIR}/domain/tasks')],
    force=True,
)
