from typing import List
from fastapi.encoders import jsonable_encoder
from pydantic import parse_obj_as
from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from src.posts.models import Post
from src.posts.schemas import PostReadSchema
from src.posts.utils import check_for_post_author


async def create_post(
        post: dict,
        session: AsyncSession,
        user_info: dict,
) -> JSONResponse:
    stmt = insert(Post).values(**post, user_id=user_info.get('user_id')) \
                       .returning(
        Post.id, Post.image, Post.title, Post.content, Post.published, Post.user_id, Post.created_at
    )
    result = await session.execute(stmt)
    await session.commit()
    data = parse_obj_as(PostReadSchema, result.one())
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder(data)
    )


async def get_posts(
        session: AsyncSession,
        pagination_params: dict
) -> JSONResponse:
    query = select(Post).where(Post.published == True) \
        .limit(pagination_params.get('limit')) \
        .offset(pagination_params.get('offset'))
    result = await session.execute(query)
    data = parse_obj_as(List[PostReadSchema], result.scalars().all())
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(data)
    )


async def get_post(
        post_id: int,
        session: AsyncSession
) -> JSONResponse:
    query = select(Post).where(Post.id == post_id, Post.published == True)
    result = await session.execute(query)
    result = result.scalar()
    if not result:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=None
        )
    data = parse_obj_as(PostReadSchema, result)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(data)
    )


async def edit_post(
        post_id: int,
        update_data: dict,
        session: AsyncSession,
        user_info: dict,
) -> JSONResponse:
    await check_for_post_author(post_id, session, user_info)
    stmt = update(Post).where(Post.id == post_id).values(**update_data) \
        .returning(
        Post.id, Post.image, Post.title, Post.content, Post.published, Post.user_id, Post.created_at
    )
    result = await session.execute(stmt)
    await session.commit()
    data = parse_obj_as(PostReadSchema, result.one())
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(data)
    )


async def delete_post(
        post_id: int,
        session: AsyncSession,
        user_info: dict
) -> JSONResponse:
    await check_for_post_author(post_id, session, user_info)
    stmt = delete(Post).where(Post.id == post_id)
    await session.execute(stmt)
    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content=None
    )
