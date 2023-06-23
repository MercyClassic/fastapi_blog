from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_async_session

from src.accounts.auth import get_current_user_info
from src.posts.services import post_service
from src.posts.schemas import (
    PostCreateSchema,
    PostUpdateSchema
)
from src.utils.utils import get_pagination_params


router = APIRouter(
    prefix='/posts',
    tags=['Posts'],
)


@router.post('')
async def create_post(
        post: PostCreateSchema,
        session: AsyncSession = Depends(get_async_session),
        user_info: dict = Depends(get_current_user_info)
):
    response = await post_service.create_post(post.dict(), session, user_info)
    return response


@router.get('/user/{user_id}')
async def get_user_posts(
        user_id: int,
        session: AsyncSession = Depends(get_async_session),
        pagination_params: dict = Depends(get_pagination_params)
):
    response = await post_service.get_user_posts(user_id, session, pagination_params)
    return response


@router.get('')
async def get_posts(
        session: AsyncSession = Depends(get_async_session),
        pagination_params: dict = Depends(get_pagination_params)
):
    response = await post_service.get_posts(session, pagination_params)
    return response


@router.get('/{post_id}')
async def get_post(
        post_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    response = await post_service.get_post(post_id, session)
    return response


@router.patch('/{post_id}')
async def edit_post(
        post_id: int,
        update_data: PostUpdateSchema,
        session: AsyncSession = Depends(get_async_session),
        user_info: dict = Depends(get_current_user_info)
):
    response = await post_service.edit_post(post_id, update_data.dict(), session, user_info)
    return response


@router.delete('/{post_id}')
async def delete_post(
        post_id: int,
        session: AsyncSession = Depends(get_async_session),
        user_info: dict = Depends(get_current_user_info)
):
    response = await post_service.delete_post(post_id, session, user_info)
    return response
