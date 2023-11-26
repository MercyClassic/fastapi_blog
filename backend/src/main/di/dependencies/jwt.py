from typing import Annotated

from fastapi import Depends
from starlette.requests import Request

from domain.services.jwt import JWTService
from infrastructure.db.uow import UnitOfWorkInterface
from main.config import get_settings


def get_jwt_service(
    uow: Annotated[UnitOfWorkInterface, Depends()],
    settings: Annotated[get_settings, Depends()],
) -> JWTService:
    return JWTService(
        settings.JWT_ACCESS_SECRET_KEY,
        settings.JWT_REFRESH_SECRET_KEY,
        uow,
    )


async def get_access_token_from_headers(request: Request) -> str:
    return request.headers.get('Authorization')
