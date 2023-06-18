from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from loguru import logger
from src.accounts.router import router as router_accounts
from src.posts.router import router as router_posts


logger.add(
    'logs/errors_log.log',
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


@app.middleware('http')
async def log_unexpected_errors(request: Request, call_next):
    response = await call_next(request)
    return response


app.include_router(router_accounts)
app.include_router(router_posts)
