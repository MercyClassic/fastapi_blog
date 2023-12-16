import logging
import os
from dataclasses import dataclass
from pathlib import Path

from celery import Celery

logger = logging.getLogger(__name__)


class ConfigParseError(ValueError):
    pass


@dataclass
class Config:
    JWT_ACCESS_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    ALGORITHM: str

    SECRET_TOKEN_FOR_EMAIL: str

    REDIS_HOST: str = 'localhost'

    ROOT_DIR = '%s' % Path(__file__).parent.parent
    MEDIA_DIR = 'media/images/'

    @property
    def media_dir(self) -> str:
        return '%s/%s' % (self.ROOT_DIR, self.MEDIA_DIR)


celery_app = Celery(
    'blog',
    broker=f'redis://{Config.REDIS_HOST}:6379/0',
)
celery_app.autodiscover_tasks(
    [f'app.domain.tasks.{module}' for module in os.listdir(f'{Config.ROOT_DIR}/domain/tasks')],
    force=True,
)


def get_str_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        logger.error(f'{key} is not set')
        raise ConfigParseError(f'{key} is not set')
    return value


def load_config():
    return Config(
        JWT_ACCESS_SECRET_KEY=get_str_env('JWT_ACCESS_SECRET_KEY'),
        JWT_REFRESH_SECRET_KEY=get_str_env('JWT_REFRESH_SECRET_KEY'),
        ALGORITHM=get_str_env('ALGORITHM'),
        SECRET_TOKEN_FOR_EMAIL=get_str_env('SECRET_TOKEN_FOR_EMAIL'),
    )
