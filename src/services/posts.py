from typing import List

from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from pydantic import parse_obj_as
from sqlalchemy import delete, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.datastructures import UploadFile
from starlette.responses import JSONResponse

from models.posts import Post
from schemas.posts import PostReadBaseSchema, PostReadSchema
from utils.posts import check_for_author, query_with_prefetched_user_and_tags
from utils.upload_image import upload_image
from utils.utils import get_query_with_pagination_params


async def update_data_image_attr(data: dict) -> None:
    image = data.get('image')
    if image:
        if isinstance(image, UploadFile):
            uploaded_image_path = await upload_image(image)
            data.update({'image': uploaded_image_path})
        elif isinstance(image, str) and image == ' ':
            data.update({'image': None})
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Invalid image type',
            )
    else:
        data.pop('image')


async def create_post(
        post: dict,
        session: AsyncSession,
        user_info: dict,
) -> JSONResponse:
    await update_data_image_attr(post)
    stmt = (
        insert(Post)
        .values(**post, user_id=user_info.get('user_id'))
        .returning(
            Post.id, Post.image, Post.title, Post.content,
            Post.published, Post.user_id, Post.created_at,
        )
    )
    result = await session.execute(stmt)
    await session.commit()
    data = parse_obj_as(PostReadBaseSchema, result.one())
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder(data),
    )


async def get_user_posts(
        user_id: int,
        session: AsyncSession,
        pagination_params: dict,
) -> JSONResponse:
    query = get_query_with_pagination_params(
        query=query_with_prefetched_user_and_tags.where(Post.user_id == user_id),
        pagination_params=pagination_params,
    )
    result = await session.execute(query)
    data = result.scalars().all()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(parse_obj_as(List[PostReadSchema], data)),
    )


async def get_posts(
        session: AsyncSession,
        pagination_params: dict,
) -> JSONResponse:
    post_query = get_query_with_pagination_params(
        query=query_with_prefetched_user_and_tags.where(Post.published == True),
        pagination_params=pagination_params,
    )
    result = await session.execute(post_query)
    posts = result.scalars().all()
    data = parse_obj_as(List[PostReadSchema], posts)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(data),
    )


async def get_post(
        post_id: int,
        session: AsyncSession,
) -> JSONResponse:
    query = query_with_prefetched_user_and_tags.where(Post.id == post_id, Post.published == True)
    result = await session.execute(query)
    result = result.scalar()
    if not result:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=None,
        )
    data = parse_obj_as(PostReadSchema, result)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(data),
    )


async def edit_post(
        post_id: int,
        update_data: dict,
        session: AsyncSession,
        user_info: dict,
) -> JSONResponse:
    await check_for_author(post_id, Post, session, user_info)
    await update_data_image_attr(update_data)
    stmt = (
        update(Post)
        .where(Post.id == post_id)
        .values(**update_data)
        .returning(
            Post.id, Post.image, Post.title, Post.content,
            Post.published, Post.user_id, Post.created_at,
        )
    )
    result = await session.execute(stmt)
    await session.commit()
    data = parse_obj_as(PostReadBaseSchema, result.one())
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(data),
    )


async def delete_post(
        post_id: int,
        session: AsyncSession,
        user_info: dict,
) -> JSONResponse:
    await check_for_author(post_id, Post, session, user_info)
    stmt = delete(Post).where(Post.id == post_id)
    await session.execute(stmt)
    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content=None,
    )
