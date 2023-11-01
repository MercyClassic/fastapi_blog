import os

from celery import Celery
from pydantic import BaseSettings


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_DB: str

    JWT_ACCESS_SECRET_KEY: str = 'JWT'
    JWT_REFRESH_SECRET_KEY: str = 'JWT'
    SECRET_TOKEN_FOR_EMAIL: str = 'JWT'
    ALGORITHM: str = 'HS256'

    EMAIl_HOST: str
    EMAIL_HOST_PASSWORD: str

    REDIS_HOST: str = 'localhost'

    MEDIA_ROOT = 'media/images'

    class Config:
        env_file = '.env', '../.env'


def get_settings() -> Settings:
    return Settings()


celery_app = Celery('blog', broker=f'redis://{get_settings().REDIS_HOST}:6379/0')
celery_app.autodiscover_tasks(
    [f'tasks.{module}' for module in os.listdir('tasks')],
    force=True,
)
