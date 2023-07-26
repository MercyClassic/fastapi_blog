import os

from celery import Celery
from dotenv import load_dotenv


load_dotenv()


POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_DB = os.getenv('POSTGRES_DB')

JWT_ACCESS_SECRET_KEY = os.getenv('JWT_ACCESS_SECRET_KEY')
JWT_REFRESH_SECRET_KEY = os.getenv('JWT_REFRESH_SECRET_KEY')
SECRET_TOKEN_FOR_EMAIL = os.getenv('SECRET_TOKEN_FOR_EMAIL')

ALGORITHM = 'HS256'

EMAIl_HOST = os.getenv('EMAIl_HOST')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

REDIS_HOST = os.getenv('REDIS_HOST')

celery_app = Celery('blog', broker=f'redis://{REDIS_HOST}:6379/0')
celery_app.autodiscover_tasks(
    [f'tasks.{module}' for module in os.listdir('tasks')],
    force=True,
)

MEDIA_ROOT = 'src/media/images'

""" CHANGE TO TRUE WHEN RUN TESTS """
IS_TEST = True
