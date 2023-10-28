from fastapi import FastAPI
from loguru import logger
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from db.database import get_async_session, get_session_stub
from dependencies.jwt import get_jwt_service
from dependencies.posts import get_post_service
from dependencies.tags import get_tag_service
from dependencies.uow import get_uow
from dependencies.users import get_user_service
from routers.jwt import router as router_jwt
from routers.posts import router as router_posts
from routers.tags import router as router_tags
from routers.users import router as router_users
from services.jwt import JWTServiceInterface
from services.posts import PostServiceInterface
from services.tags import TagServiceInterface
from services.users import UserServiceInterface
from uow import UnitOfWorkInterface

logger.add(
    'logs/errors.log',
    format='{time} - {level} - {message}',
    level='ERROR',
    rotation='1 month',
    compression='zip',
)


app = FastAPI(
    title='First fastapi blog',
)

app.dependency_overrides[UnitOfWorkInterface] = get_uow
app.dependency_overrides[PostServiceInterface] = get_post_service
app.dependency_overrides[TagServiceInterface] = get_tag_service
app.dependency_overrides[UserServiceInterface] = get_user_service
app.dependency_overrides[JWTServiceInterface] = get_jwt_service
app.dependency_overrides[get_session_stub] = get_async_session

app.mount('/media', StaticFiles(directory='media'), name='media')

origins = [
    'http://localhost:3000',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'OPTIONS', 'DELETE', 'PATCH', 'PUT'],
    allow_headers=[
        'Content-Type',
        'Set-Cookie',
        'Access-Control-Allow-Headers',
        'Access-Control-Allow-Origin',
        'Authorization',
        'X-CSRFToken',
    ],
)


@app.exception_handler(Exception)
async def unexpected_error_log(request, ex):
    logger.error(ex)
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=None)


app.include_router(router_jwt)
app.include_router(router_posts)
app.include_router(router_tags)
app.include_router(router_users)
