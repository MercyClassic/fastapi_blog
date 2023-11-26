from functools import partial

from fastapi import FastAPI

from domain.services.jwt import JWTServiceInterface
from domain.services.posts import PostServiceInterface
from domain.services.tags import TagServiceInterface
from domain.services.users import UserServiceInterface
from infrastructure.db.database import (
    create_async_session_maker,
    get_async_session,
    get_session_stub,
)
from infrastructure.db.uow import UnitOfWorkInterface
from main.config import Settings
from main.di.dependencies.jwt import get_jwt_service
from main.di.dependencies.posts import get_post_service
from main.di.dependencies.tags import get_tag_service
from main.di.dependencies.uow import get_uow
from main.di.dependencies.users import get_user_service


def init_dependencies(app: FastAPI, settings: Settings) -> None:
    async_session_maker = create_async_session_maker(settings)

    app.dependency_overrides[get_session_stub] = partial(
        get_async_session,
        async_session_maker,
    )

    app.dependency_overrides[UnitOfWorkInterface] = get_uow
    app.dependency_overrides[PostServiceInterface] = get_post_service
    app.dependency_overrides[TagServiceInterface] = get_tag_service
    app.dependency_overrides[UserServiceInterface] = get_user_service
    app.dependency_overrides[JWTServiceInterface] = get_jwt_service
