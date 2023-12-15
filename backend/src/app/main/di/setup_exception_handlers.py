from functools import partial
from typing import Awaitable, Callable

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from loguru import logger
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.domain.exceptions.base import DomainException, NotFound, PermissionDenied
from app.domain.exceptions.users import (
    AccountAlreadyActivated,
    AccountIsNotActive,
    InvalidCredentials,
    InvalidImageType,
    InvalidToken,
    PasswordTooShort,
    UserAlreadyExists,
)
from app.main.config import get_settings

settings = get_settings()

logger.add(
    f'{settings.ROOT_DIR}/logs/errors.log',
    format='{time} - {level} - {message}',
    level='ERROR',
    rotation='1 month',
    compression='zip',
)


def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        DomainException,
        error_handler('Domain Error', status.HTTP_500_INTERNAL_SERVER_ERROR),
    )
    app.add_exception_handler(
        NotFound,
        error_handler('Not Found', status.HTTP_404_NOT_FOUND),
    )
    app.add_exception_handler(
        PermissionDenied,
        error_handler('Permission Denied', status.HTTP_403_FORBIDDEN),
    )
    app.add_exception_handler(
        AccountAlreadyActivated,
        error_handler('Account already activated', status.HTTP_403_FORBIDDEN),
    )
    app.add_exception_handler(
        UserAlreadyExists,
        error_handler('User already exists', status.HTTP_403_FORBIDDEN),
    )
    app.add_exception_handler(
        InvalidToken,
        error_handler('Invalid Token', status.HTTP_403_FORBIDDEN),
    )
    app.add_exception_handler(
        AccountIsNotActive,
        error_handler('Account is not activated', status.HTTP_403_FORBIDDEN),
    )
    app.add_exception_handler(
        InvalidCredentials,
        error_handler('Invalid credentials', status.HTTP_422_UNPROCESSABLE_ENTITY),
    )
    app.add_exception_handler(
        InvalidImageType,
        error_handler('Invalid image type', status.HTTP_422_UNPROCESSABLE_ENTITY),
    )
    app.add_exception_handler(
        PasswordTooShort,
        error_handler(
            'Password length must be over 4 symbols',
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ),
    )
    app.add_exception_handler(
        Exception,
        unknown_exception_handler,
    )


def error_handler(info: str, status_code: int) -> Callable[..., Awaitable[JSONResponse]]:
    return partial(
        domain_error_handler,
        info=info,
        status_code=status_code,
    )


async def domain_error_handler(
    request: Request,
    ex: DomainException,
    info: str,
    status_code: int,
) -> JSONResponse:
    logger.error(ex)
    return JSONResponse(
        jsonable_encoder({'error': {'info': info}}),
        status_code=status_code,
    )


async def unknown_exception_handler(
    request: Request,
    ex: Exception,
) -> JSONResponse:
    logger.error(ex)
    return JSONResponse(
        content=None,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
