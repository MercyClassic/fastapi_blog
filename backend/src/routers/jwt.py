from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from schemas.jwt import AuthenticateSchema
from services.jwt import JWTServiceInterface
from services.users import UserServiceInterface
from uow import UnitOfWorkInterface

router = APIRouter(
    prefix='/api/v1/auth',
    tags=['JWT'],
)


@router.post('/login')
async def login(
    authenticate_data: AuthenticateSchema,
    jwt_service: Annotated[JWTServiceInterface, Depends()],
    uow: Annotated[UnitOfWorkInterface, Depends()],
    user_service: Annotated[UserServiceInterface, Depends()],
):
    user_id = await user_service.authenticate(uow, **authenticate_data.dict())
    tokens = await jwt_service.create_auth_tokens(user_id, uow)
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={'access_token': tokens['access_token']},
    )
    response.set_cookie(
        key='refresh_token',
        value=tokens['refresh_token'],
        httponly=True,
        max_age=60 * 60 * 24 * 7,
    )
    return response


@router.post('/refresh_token')
async def refresh_access_token(
    request: Request,
    jwt_service: Annotated[JWTServiceInterface, Depends()],
    uow: Annotated[UnitOfWorkInterface, Depends()],
):
    tokens = await jwt_service.refresh_auth_tokens(request.cookies.get('refresh_token'), uow)
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={'access_token': tokens['access_token']},
    )
    response.set_cookie(
        key='refresh_token',
        value=tokens['refresh_token'],
        httponly=True,
        max_age=60 * 60 * 24 * 7,
    )
    return response


@router.post('/logout')
async def logout(
    request: Request,
    jwt_service: Annotated[JWTServiceInterface, Depends()],
    uow: Annotated[UnitOfWorkInterface, Depends()],
):
    await jwt_service.delete_refresh_token(request.cookies.get('refresh_token'), uow)
    response = JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=None)
    response.delete_cookie('refresh_token')
    return response
