from typing import Annotated

from fastapi import Depends

from app.domain.services.users import UserService
from app.infrastructure.db.uow import UnitOfWorkInterface


def get_user_service(
    uow: Annotated[UnitOfWorkInterface, Depends()],
) -> UserService:
    return UserService(uow)
