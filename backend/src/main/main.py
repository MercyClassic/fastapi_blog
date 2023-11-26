from fastapi import FastAPI
from loguru import logger
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from main.config import get_settings
from main.di.init_dependencies import init_dependencies
from presentators.api.routers.root import root_router

settings = get_settings()


logger.add(
    f'{settings.ROOT_DIR}/logs/errors.log',
    format='{time} - {level} - {message}',
    level='ERROR',
    rotation='1 month',
    compression='zip',
)


def create_app() -> FastAPI:
    app = FastAPI(
        title='First fastapi blog',
    )
    init_dependencies(app, settings)
    return app


app = create_app()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:3000',
    ],
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


app.include_router(root_router)
