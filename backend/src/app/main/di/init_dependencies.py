from functools import partial

from fastapi import FastAPI

from app.application.interfaces.encoders.jwt import JWTEncoderInterface
from app.domain.interfaces.users import (
    SendVerifyMessageServiceInterface,
    UserVerifyServiceInterface,
)
from app.domain.services.jwt import JWTServiceInterface
from app.domain.services.posts import PostServiceInterface
from app.domain.services.tags import TagServiceInterface
from app.domain.services.users import UserServiceInterface
from app.infrastructure.db.database import (
    create_async_session_maker,
    get_async_session,
    get_session_stub,
)
from app.infrastructure.db.uow import UnitOfWorkInterface
from app.main.config import Config, load_config
from app.main.di.dependencies.jwt import get_jwt_encoder, get_jwt_service
from app.main.di.dependencies.posts import get_post_service
from app.main.di.dependencies.tags import get_tag_service
from app.main.di.dependencies.uow import get_uow
from app.main.di.dependencies.users import (
    get_send_verify_message_service,
    get_user_service,
    get_user_verify_service,
)


def init_dependencies(app: FastAPI, db_uri: str) -> None:
    async_session_maker = create_async_session_maker(db_uri)

    app.dependency_overrides[get_session_stub] = partial(
        get_async_session,
        async_session_maker,
    )

    app.dependency_overrides[UnitOfWorkInterface] = get_uow
    app.dependency_overrides[PostServiceInterface] = get_post_service
    app.dependency_overrides[TagServiceInterface] = get_tag_service
    app.dependency_overrides[UserServiceInterface] = get_user_service
    app.dependency_overrides[SendVerifyMessageServiceInterface] = get_send_verify_message_service
    app.dependency_overrides[UserVerifyServiceInterface] = get_user_verify_service
    app.dependency_overrides[JWTServiceInterface] = get_jwt_service
    app.dependency_overrides[JWTEncoderInterface] = get_jwt_encoder
    app.dependency_overrides[Config] = load_config
