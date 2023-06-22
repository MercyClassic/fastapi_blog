from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only, joinedload, selectinload
from starlette import status
from starlette.exceptions import HTTPException

from src.posts.models import Post


async def check_for_post_author(
        post_id: int,
        session: AsyncSession,
        user_info: dict
) -> None:
    query = select(Post).where(Post.id == post_id).options(load_only(Post.user_id))
    post = await session.execute(query)
    post_info = post.scalar()
    if not post_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=None
        )
    if user_info.get('user_id') != post_info.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=None
        )


query_with_prefetched_user_and_tags = (
    select(Post)
    .options(joinedload(Post.user))
    .options(selectinload(Post.tags))
)
