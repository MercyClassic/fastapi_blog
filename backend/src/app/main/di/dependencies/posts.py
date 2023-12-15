from typing import Annotated

from fastapi import Depends

from app.domain.services.posts import PostService
from app.infrastructure.db.uow import UnitOfWorkInterface


def get_post_service(
    uow: Annotated[UnitOfWorkInterface, Depends()],
) -> PostService:
    return PostService(uow)
