from typing import List
from fastapi.encoders import jsonable_encoder
from pydantic import parse_obj_as
from sqlalchemy import insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from src.utils.utils import get_query_with_limit_and_offset_params
from src.posts.models import Post
from src.posts.schemas import PostReadSchema, PostReadBaseSchema
from src.posts.utils import (
    check_for_author,
    query_with_prefetched_user_and_tags
)


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
    data = parse_obj_as(PostReadBaseSchema, result.one())
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder(data)
    )


async def get_user_posts(
        user_id: int,
        session: AsyncSession,
        pagination_params: dict
) -> JSONResponse:
    query = get_query_with_limit_and_offset_params(
        query=query_with_prefetched_user_and_tags.where(Post.user_id == user_id),
        pagination_params=pagination_params
    )
    result = await session.execute(query)
    data = result.scalars().all()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(parse_obj_as(List[PostReadSchema], data))
    )


async def get_posts(
        session: AsyncSession,
        pagination_params: dict
) -> JSONResponse:
    post_query = get_query_with_limit_and_offset_params(
        query=query_with_prefetched_user_and_tags.where(Post.published == True),
        pagination_params=pagination_params
    )
    result = await session.execute(post_query)
    posts = result.scalars().all()
    data = parse_obj_as(List[PostReadSchema], posts)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(data)
    )


async def get_post(
        post_id: int,
        session: AsyncSession
) -> JSONResponse:
    query = query_with_prefetched_user_and_tags.where(Post.id == post_id, Post.published == True)
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
    await check_for_author(post_id, Post, session, user_info)
    stmt = update(Post).where(Post.id == post_id).values(**update_data) \
        .returning(
        Post.id, Post.image, Post.title, Post.content, Post.published, Post.user_id, Post.created_at
    )
    result = await session.execute(stmt)
    await session.commit()
    data = parse_obj_as(PostReadBaseSchema, result.one())
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(data)
    )


async def delete_post(
        post_id: int,
        session: AsyncSession,
        user_info: dict
) -> JSONResponse:
    await check_for_author(post_id, Post, session, user_info)
    stmt = delete(Post).where(Post.id == post_id)
    await session.execute(stmt)
    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content=None
    )
