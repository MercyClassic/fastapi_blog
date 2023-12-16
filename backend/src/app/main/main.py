import os

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.main.di.init_dependencies import init_dependencies
from app.main.exceptions.setup_exception_handlers import setup_exception_handlers
from app.presentators.api.routers.root import root_router


def create_app() -> FastAPI:
    app = FastAPI(
        title='First fastapi blog',
    )
    init_dependencies(app, os.environ['db_uri'])
    app.include_router(root_router)
    setup_exception_handlers(app)
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
