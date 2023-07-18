from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only, selectinload
from starlette import status
from starlette.exceptions import HTTPException

from models.posts import Post, Tag
from models.users import User


async def check_for_author(
        item_id: int,
        model,
        session: AsyncSession,
        user_info: dict,
) -> None:
    query = select(model).where(model.id == item_id).options(load_only(model.user_id))
    instance = await session.execute(query)
    instance_info = instance.scalar()
    if not instance_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=None,
        )
    if user_info.get('user_id') != instance_info.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=None,
        )


query_with_prefetched_user_and_tags = (
    select(Post)
    .options(
        load_only(Post.id, Post.title, Post.content, Post.created_at, Post.published, Post.image),
    )
    .options(
        joinedload(Post.user)
        .options(load_only(User.id, User.username)),
    )
    .options(
        selectinload(Post.tags)
        .options(load_only(Tag.id, Tag.name, Tag.created_at)),
    )
)
