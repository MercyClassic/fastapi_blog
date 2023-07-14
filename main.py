from fastapi import FastAPI
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from loguru import logger
from starlette.responses import JSONResponse

from src.routers.users import router as router_users
from src.routers.posts import router as router_posts
from src.routers.tags import router as router_tags


logger.add(
    'src/logs/errors_log.log',
    format='{time} - {level} - {message}',
    level='ERROR',
    rotation='1 month',
    compression='zip',
)


app = FastAPI(
    title='First fastapi blog'
)

origins = [
    'http://127.0.0.1:8000',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
)


@app.exception_handler(Exception)
async def unexpected_error_log(request, ex):
    logger.error(ex)
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=None)


app.include_router(router_users)
app.include_router(router_posts)
app.include_router(router_tags)
