from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_async_session
from repositories.tags import TagRepository
from services.tags import TagService
from utils.utils import get_pagination_params


def get_tag_service(
        session: AsyncSession = Depends(get_async_session),
        pagination_params: dict = Depends(get_pagination_params),
):
    return TagService(TagRepository(session, pagination_params))
