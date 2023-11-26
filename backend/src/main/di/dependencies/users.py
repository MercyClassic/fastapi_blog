from typing import Annotated

from fastapi import Depends

from domain.services.users import UserService
from infrastructure.db.uow import UnitOfWorkInterface


def get_user_service(
    uow: Annotated[UnitOfWorkInterface, Depends()],
) -> UserService:
    return UserService(uow)
