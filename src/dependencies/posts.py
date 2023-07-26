from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_async_session
from repositories.posts import PostRepository
from services.posts import PostService
from utils.utils import get_pagination_params


def get_post_service(
        session: AsyncSession = Depends(get_async_session),
        pagination_params: dict = Depends(get_pagination_params),
):
    return PostService(PostRepository(session, pagination_params))
