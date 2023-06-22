from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_async_session

from src.accounts.auth import get_current_user_info
from src.posts import services
from src.posts.schemas import (
    PostCreateSchema,
    PostUpdateSchema,
    TagCreateSchema,
    SetPostTagSchema
)
from src.utils.utils import get_pagination_params


router = APIRouter(
    prefix='/posts',
    tags=['Posts'],
)


@router.get('/tags')
async def get_tags(
        session: AsyncSession = Depends(get_async_session),
        pagination_params: dict = Depends(get_pagination_params)
):
    response = await services.get_tags(session, pagination_params)
    return response


@router.post('/tags')
async def create_tag(
        tag: TagCreateSchema,
        session: AsyncSession = Depends(get_async_session)
):
    response = await services.create_tag(tag, session)
    return response


@router.get('/{post_id}/tags')
async def get_post_tags(
        post_id: int,
        session: AsyncSession = Depends(get_async_session),
        pagination_params: dict = Depends(get_pagination_params)
):
    response = await services.get_post_tags(post_id, session, pagination_params)
    return response


@router.post('/{post_id}/tags')
async def set_post_tag(
        data: SetPostTagSchema,
        session: AsyncSession = Depends(get_async_session)
):
    response = await services.set_post_tag(data, session)
    return response


@router.post('')
async def create_post(
        post: PostCreateSchema,
        session: AsyncSession = Depends(get_async_session),
        user_info: dict = Depends(get_current_user_info)
):
    response = await services.create_post(post.dict(), session, user_info)
    return response


@router.get('/user/{user_id}')
async def get_user_posts(
        user_id: int,
        session: AsyncSession = Depends(get_async_session),
        pagination_params: dict = Depends(get_pagination_params)
):
    response = await services.get_user_posts(user_id, session, pagination_params)
    return response


@router.get('')
async def get_posts(
        session: AsyncSession = Depends(get_async_session),
        pagination_params: dict = Depends(get_pagination_params)
):
    response = await services.get_posts(session, pagination_params)
    return response


@router.get('/{post_id}')
async def get_post(
        post_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    response = await services.get_post(post_id, session)
    return response


@router.patch('/{post_id}')
async def edit_post(
        post_id: int,
        update_data: PostUpdateSchema,
        session: AsyncSession = Depends(get_async_session),
        user_info: dict = Depends(get_current_user_info)
):
    response = await services.edit_post(post_id, update_data.dict(), session, user_info)
    return response


@router.delete('/{post_id}')
async def delete_post(
        post_id: int,
        session: AsyncSession = Depends(get_async_session),
        user_info: dict = Depends(get_current_user_info)
):
    response = await services.delete_post(post_id, session, user_info)
    return response


