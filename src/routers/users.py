from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from pydantic import parse_obj_as
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse
from src.db.database import get_async_session

from src.utils.utils import get_pagination_params
from src.services import users as service
from src.auth.auth import get_current_user_info
from src.managers.users import UserManager
from src.schemas.users import (
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
        user_info: dict = Depends(get_current_user_info),
        pagination_params: dict = Depends(get_pagination_params)
) -> JSONResponse:
    response = await service.get_users(session, user_info, pagination_params)
    return response


@router.get('/{user_id}', dependencies=[Depends(get_current_user_info)])
async def get_user(
        user_id: int,
        session: AsyncSession = Depends(get_async_session),
) -> JSONResponse:
    response = await service.get_user(user_id, session)
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


@router.get('/activate/{verify_token}')
async def verify_account(
        verify_token: str,
        session: AsyncSession = Depends(get_async_session)
):
    await UserManager.verify(verify_token, session)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=None
    )


@router.post('/auth/login')
async def login(
        authenticate_data: AuthenticateSchema,
        session: AsyncSession = Depends(get_async_session)
):
    user_id = await UserManager.authenticate(**authenticate_data.dict(), session=session)
    if user_id:
        tokens = await UserManager.create_auth_tokens(user_id, session)
        response = JSONResponse(status_code=status.HTTP_200_OK, content=None)
        response.set_cookie(key='access_token', value=tokens.get('access_token'))
        response.set_cookie(key='refresh_token', value=tokens.get('refresh_token'), httponly=True)
        return response
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=None)


@router.post('/auth/refresh_token')
async def refresh_access_token(
        request: Request,
        session: AsyncSession = Depends(get_async_session)
):
    tokens = await UserManager.refresh_access_token(request.cookies.get('refresh_token'), session)
    response = JSONResponse(status_code=status.HTTP_200_OK, content=None)
    response.set_cookie(key='access_token', value=tokens.get('access_token'), httponly=True)
    response.set_cookie(key='refresh_token', value=tokens.get('refresh_token'), httponly=True)
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
