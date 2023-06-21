from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from pydantic import parse_obj_as
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse
from src.db.database import get_async_session

from src.accounts import services
from src.accounts.auth import get_current_user_info
from src.accounts.manager import UserManager
from src.accounts.schemas import (
    UserCreateSchema,
    UserReadBaseSchema,
    AuthenticateSchema
)


router = APIRouter(
    prefix='/users',
    tags=['Accounts']
)


@router.get('')
async def get_users(
        session: AsyncSession = Depends(get_async_session),
        user_info: dict = Depends(get_current_user_info)
) -> JSONResponse:
    response = await services.get_users(session, user_info)
    return response


@router.get('/{user_id}')
async def get_user(
        user_id: int,
        session: AsyncSession = Depends(get_async_session),
) -> JSONResponse:
    response = await services.get_user(user_id, session)
    return response


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
