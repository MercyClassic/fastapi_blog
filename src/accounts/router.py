from typing import List
from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from pydantic import parse_obj_as
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.accounts.auth import get_current_user
from src.accounts.manager import UserManager
from src.db.database import get_async_session
from src.accounts.schemas import (
    UserCreateSchema,
    UserReadBaseSchema,
    UserReadSchemaForAdmin,
    AuthenticateSchema
)
from src.accounts.models import User


router = APIRouter(
    prefix='/users',
    tags=['Accounts']
)


@router.get('/')
async def get_users(
        request: Request,
        session: AsyncSession = Depends(get_async_session),
) -> JSONResponse:
    user = await get_current_user(request.cookies.get('access_token'), session)
    fields = [User.id, User.email, User.username]
    if user.is_superuser:
        fields += [User.registered_at, User.is_superuser, User.is_active, User.is_verified]
    query = select(User).where(User.is_active == True).options(load_only(*fields))
    result = await session.execute(query)
    schema = UserReadSchemaForAdmin if user.is_superuser else UserReadBaseSchema
    data = parse_obj_as(List[schema], result.scalars().all())
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(data)
    )


@router.get('/{user_id}')
async def get_user(
        session: AsyncSession = Depends(get_async_session),
        user_id: int = None,
) -> JSONResponse:
    query = select(User).where(User.id == user_id).options(load_only(User.id, User.username, User.email))
    result = await session.execute(query)
    result = result.scalar()
    if result is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=None
        )
    data = parse_obj_as(UserReadBaseSchema, result)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(data)
    )


@router.post('/register')
async def registration(
        user_input_data: UserCreateSchema,
        session: AsyncSession = Depends(get_async_session)
) -> JSONResponse:
    user = await UserManager.create_user(user_input_data=user_input_data, session=session)
    data = parse_obj_as(UserReadBaseSchema, user)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder(data)
    )


@router.post('/auth/login')
async def login(
        authenticate_data: AuthenticateSchema,
        session: AsyncSession = Depends(get_async_session)
):
    user_id = await UserManager.authenticate(**authenticate_data.dict(), session=session)
    if user_id:
        tokens = await UserManager.create_jwt_tokens(user_id, session)
        response = JSONResponse(status_code=status.HTTP_200_OK, content=None)
        for k, v in tokens.items():
            response.set_cookie(key=k, value=v)
        return response
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=None)


@router.post('/auth/refresh_token')
async def refresh_access_token(
        request: Request,
        session: AsyncSession = Depends(get_async_session)
):
    tokens = await UserManager.refresh_access_token(request.cookies.get('refresh_token'), session)
    response = JSONResponse(status_code=status.HTTP_200_OK, content=None)
    for k, v in tokens.items():
        response.set_cookie(key=k, value=v)
    return response


@router.post('/auth/logout')
async def logout(
        request: Request,
        session: AsyncSession = Depends(get_async_session)
):
    await UserManager.delete_current_refresh_token(request.cookies.get('refresh_token'), session)
    response = JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=None)
    response.delete_cookie('refresh_token')
    response.delete_cookie('access_token')
    return response
