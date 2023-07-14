from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_async_session

from src.auth.auth import get_current_user_info
from src.services import tags as tag_service
from src.schemas.posts import (
    TagCreateSchema,
    PostTagBaseSchema,
    TagUpdateSchema
)
from src.utils.utils import get_pagination_params


router = APIRouter(
    prefix='/tags',
    tags=['Tags'],
)


@router.get('')
async def get_tags(
        session: AsyncSession = Depends(get_async_session),
        pagination_params: dict = Depends(get_pagination_params)
):
    response = await tag_service.get_tags(session, pagination_params)
    return response


@router.post('')
async def create_tag(
        tag: TagCreateSchema,
        session: AsyncSession = Depends(get_async_session),
        user_info: dict = Depends(get_current_user_info)
):
    response = await tag_service.create_tag(tag, session, user_info)
    return response


@router.delete('/{tag_id}')
async def delete_tag(
        tag_id: int,
        session: AsyncSession = Depends(get_async_session),
        user_info: dict = Depends(get_current_user_info)
):
    response = await tag_service.delete_tag(tag_id, session, user_info)
    return response


@router.patch('/{tag_id}')
async def edit_tag(
        tag_id: int,
        update_data: TagUpdateSchema,
        session: AsyncSession = Depends(get_async_session),
        user_info: dict = Depends(get_current_user_info)
):
    response = await tag_service.edit_tag(tag_id, update_data, session, user_info)
    return response


@router.get('/post/{post_id}')
async def get_post_tags(
        post_id: int,
        session: AsyncSession = Depends(get_async_session),
        pagination_params: dict = Depends(get_pagination_params)
):
    response = await tag_service.get_post_tags(post_id, session, pagination_params)
    return response


@router.post('/post/{post_id}')
async def set_post_tag(
        post_id: int,
        data: PostTagBaseSchema,
        session: AsyncSession = Depends(get_async_session),
        user_info: dict = Depends(get_current_user_info)
):
    response = await tag_service.set_post_tag(post_id, data, session, user_info)
    return response


@router.delete('/posttag/{posttag_id}')
async def delete_post_tag(
        posttag_id: int,
        session: AsyncSession = Depends(get_async_session),
        user_info: dict = Depends(get_current_user_info)
):
    response = await tag_service.delete_post_tag(posttag_id, session, user_info)
    return response
