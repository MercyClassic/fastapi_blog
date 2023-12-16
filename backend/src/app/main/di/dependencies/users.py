from typing import Annotated

from fastapi import Depends

from app.application.interfaces.encoders.jwt import JWTEncoderInterface
from app.domain.services.users import (
    SendVerifyMessageService,
    UserService,
    UserVerifyService,
)
from app.infrastructure.db.uow import UnitOfWorkInterface
from app.main.config import Config
from app.main.di.stub import Stub


def get_user_service(
    uow: Annotated[UnitOfWorkInterface, Depends()],
) -> UserService:
    return UserService(uow)


def get_send_verify_message_service(
    jwt_encoder: Annotated[JWTEncoderInterface, Depends()],
    config: Annotated[Config, Depends(Stub(Config))],
):
    return SendVerifyMessageService(jwt_encoder, config.SECRET_TOKEN_FOR_EMAIL)


def get_user_verify_service(
    uow: Annotated[UnitOfWorkInterface, Depends()],
    jwt_encoder: Annotated[JWTEncoderInterface, Depends()],
    config: Annotated[Config, Depends(Stub(Config))],
):
    return UserVerifyService(uow, jwt_encoder, config.SECRET_TOKEN_FOR_EMAIL)
