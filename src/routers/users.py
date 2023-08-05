from typing import List

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from pydantic import parse_obj_as
from starlette import status
from starlette.responses import JSONResponse

from auth.auth import get_current_user_info
from schemas.users import (
    UserCreateSchema,
    UserReadBaseSchema, UserReadSchemaForAdmin,
)
from services.users import UserService
from dependencies.users import get_user_service


router = APIRouter(
    prefix='/users',
    tags=['Accounts'],
)


@router.get('')
async def get_users(
        user_info: dict = Depends(get_current_user_info),
        user_service: UserService = Depends(get_user_service),
) -> JSONResponse:
    users = await user_service.get_users(user_info)
    schema = UserReadSchemaForAdmin if user_info.get('is_superuser') else UserReadBaseSchema
    data = jsonable_encoder(
        parse_obj_as(List[schema], users),
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=data,
    )


@router.get('/{user_id}', dependencies=[Depends(get_current_user_info)])
async def get_user(
        user_id: int,
        user_info: dict = Depends(get_current_user_info),
        user_service: UserService = Depends(get_user_service),
) -> JSONResponse:
    user = await user_service.get_user(user_info, user_id)
    schema = UserReadSchemaForAdmin if user_info.get('is_superuser') else UserReadBaseSchema
    data = jsonable_encoder(parse_obj_as(schema, user))
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=data,
    )


@router.post('/register')
async def registration(
        user_data: UserCreateSchema,
        user_service: UserService = Depends(get_user_service),
) -> JSONResponse:
    user = await user_service.create_user(user_data=user_data.dict())
    data = jsonable_encoder(
        parse_obj_as(UserReadBaseSchema, user),
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=data,
    )


@router.get('/activate/{verify_token}')
async def verify_account(
        verify_token: str,
        user_service: UserService = Depends(get_user_service),
):
    await user_service.verify(verify_token)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=None,
    )
