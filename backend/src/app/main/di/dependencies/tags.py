from typing import Annotated

from fastapi import Depends

from app.domain.services.tags import TagService
from app.infrastructure.db.uow import UnitOfWorkInterface


def get_tag_service(
    uow: Annotated[UnitOfWorkInterface, Depends()],
) -> TagService:
    return TagService(uow)
