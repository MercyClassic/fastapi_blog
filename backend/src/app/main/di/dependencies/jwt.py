from typing import Annotated

from fastapi import Depends

from app.application.auth.encoders.jwt import JWTEncoder
from app.application.interfaces.encoders.jwt import JWTEncoderInterface
from app.domain.services.jwt import JWTService
from app.infrastructure.db.interfaces.repositories.uow import UnitOfWorkInterface
from app.main.config import Config
from app.main.di.stub import Stub


def get_jwt_service(
    uow: Annotated[UnitOfWorkInterface, Depends()],
    jwt_encoder: Annotated[JWTEncoderInterface, Depends()],
    settings: Annotated[Config, Depends(Stub(Config))],
) -> JWTService:
    return JWTService(
        jwt_encoder,
        settings.JWT_ACCESS_SECRET_KEY,
        settings.JWT_REFRESH_SECRET_KEY,
        uow,
    )


def get_jwt_encoder(
    config: Annotated[Config, Depends(Stub(Config))],
):
    return JWTEncoder(
        config.ALGORITHM,
    )
