from typing import List

from fastapi.encoders import jsonable_encoder
from pydantic import parse_obj_as
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only
from starlette import status
from starlette.responses import JSONResponse

from models.posts import Post, PostTag, Tag
from schemas.posts import (PostTagBaseSchema, PostTagReadSchema,
                           TagCreateSchema, TagReadSchema, TagUpdateSchema)
from utils.posts import check_for_author
from utils.utils import get_query_with_pagination_params


async def get_tags(
        session: AsyncSession,
        pagination_params: dict,
) -> JSONResponse:
    query = get_query_with_pagination_params(
        query=select(Tag),
        pagination_params=pagination_params,
    )
    result = await session.execute(query)
    tags = result.scalars().all()
    data = parse_obj_as(List[TagReadSchema], tags)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(data),
    )


async def create_tag(
        tag: TagCreateSchema,
        session: AsyncSession,
        user_info: dict,
) -> JSONResponse:
    stmt = (
        insert(Tag)
        .values(**tag.dict(), user_id=user_info.get('user_id'))
        .returning(Tag.id, Tag.name, Tag.created_at)
    )
    result = await session.execute(stmt)
    await session.commit()
    tag = result.one()
    data = parse_obj_as(TagReadSchema, tag)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder(data),
    )


async def delete_tag(
        tag_id: int,
        session: AsyncSession,
        user_info: dict,
) -> JSONResponse:
    await check_for_author(tag_id, Tag, session, user_info)
    stmt = delete(Tag).where(Tag.id == tag_id)
    await session.execute(stmt)
    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content=None,
    )


async def edit_tag(
        tag_id: int,
        update_data: TagUpdateSchema,
        session: AsyncSession,
        user_info: dict,
) -> JSONResponse:
    await check_for_author(tag_id, Tag, session, user_info)
    stmt = (
        update(Tag)
        .where(Tag.id == tag_id)
        .values(**update_data.dict())
        .returning(Tag.id, Tag.name, Tag.created_at)
    )
    result = await session.execute(stmt)
    await session.commit()

    try:
        data = parse_obj_as(TagReadSchema, result.one())
    except NoResultFound:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=None,
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(data),
    )


async def get_post_tags(
        post_id: int,
        session: AsyncSession,
        pagination_params: dict,
) -> JSONResponse:
    query = get_query_with_pagination_params(
        query=(
            select(Tag)
            .options(load_only(Tag.id, Tag.name, Tag.created_at))
            .join(PostTag)
            .join(Post)
            .where(PostTag.post_id == post_id, Post.published is True)
        ),
        pagination_params=pagination_params,
    )
    result = await session.execute(query)
    tags = result.scalars().all()
    data = parse_obj_as(List[TagReadSchema], tags)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(data),
    )


async def set_post_tag(
        post_id: int,
        data: PostTagBaseSchema,
        session: AsyncSession,
        user_info: dict,
) -> JSONResponse:
    await check_for_author(post_id, Post, session, user_info)
    stmt = (
        insert(PostTag)
        .values(**data.dict(), post_id=post_id)
        .returning(PostTag.id, PostTag.post_id, PostTag.tag_id)
    )
    result = await session.execute(stmt)
    await session.commit()
    result = result.one()
    data = parse_obj_as(PostTagReadSchema, result)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder(data),
    )


async def delete_post_tag(
        posttag_id: int,
        session: AsyncSession,
        user_info: dict,
) -> JSONResponse:
    query = (
        select(Post)
        .join(PostTag)
        .where(PostTag.id == posttag_id)
        .options(load_only(Post.user_id))
    )
    result = await session.execute(query)
    instance = result.scalar()
    if not instance:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=None,
        )
    if instance.user_id != user_info.get('user_id'):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=None,
        )
    stmt = delete(PostTag).where(PostTag.id == posttag_id)
    await session.execute(stmt)
    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content=None,
    )
