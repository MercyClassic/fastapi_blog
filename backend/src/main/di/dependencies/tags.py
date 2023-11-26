from typing import Annotated

from fastapi import Depends

from domain.services.tags import TagService
from infrastructure.db.uow import UnitOfWorkInterface


def get_tag_service(
    uow: Annotated[UnitOfWorkInterface, Depends()],
) -> TagService:
    return TagService(uow)
