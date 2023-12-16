from typing import Annotated

from fastapi import Depends
from starlette.requests import Request

from app.application.interfaces.encoders.jwt import JWTEncoderInterface
from app.domain.managers.users import UserManager
from app.main.config import Config
from app.main.di.stub import Stub


async def get_access_token_from_headers(request: Request) -> str:
    return request.headers.get('Authorization')


async def get_current_user_info(
    access_token: Annotated[str, Depends(get_access_token_from_headers)],
    jwt_encoder: Annotated[JWTEncoderInterface, Depends()],
    config: Annotated[Config, Depends(Stub(Config))],
) -> dict:
    user_manager = UserManager(config.JWT_ACCESS_SECRET_KEY, jwt_encoder)
    return user_manager.get_user_info_from_access_token(access_token)
