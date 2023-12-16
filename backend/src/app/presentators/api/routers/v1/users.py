from typing import Annotated, List

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from pydantic import parse_obj_as
from starlette import status
from starlette.responses import JSONResponse

from app.application.models.users import (
    UserCreateSchema,
    UserReadBaseSchema,
    UserReadSchemaForAdmin,
)
from app.domain.interfaces.users import (
    SendVerifyMessageServiceInterface,
    UserVerifyServiceInterface,
)
from app.domain.services.users import UserServiceInterface
from app.main.di.dependencies.auth import get_current_user_info

router = APIRouter(
    prefix='/users',
    tags=['Accounts'],
)


@router.get('')
async def get_users(
    user_info: Annotated[dict, Depends(get_current_user_info)],
    user_service: Annotated[UserServiceInterface, Depends()],
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


@router.get('/{user_id}')
async def get_user(
    user_id: int,
    user_info: Annotated[dict, Depends(get_current_user_info)],
    user_service: Annotated[UserServiceInterface, Depends()],
) -> JSONResponse:
    user = await user_service.get_user(user_info, user_id)
    schema = UserReadSchemaForAdmin if user_info.get('is_superuser') else UserReadBaseSchema
    data = jsonable_encoder(parse_obj_as(schema, user))
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=data,
    )


@router.post('')
async def registration(
    user_data: UserCreateSchema,
    user_service: Annotated[UserServiceInterface, Depends()],
    send_verify_message_service: Annotated[SendVerifyMessageServiceInterface, Depends()],
) -> JSONResponse:
    user_data = await user_service.create_user(user_data.dict())
    send_verify_message_service.send_verify_message(user_data)
    data = jsonable_encoder(
        parse_obj_as(UserReadBaseSchema, user_data),
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=data,
    )


@router.get('/activate/{verify_token}')
async def verify_account(
    verify_token: str,
    user_verify_service: Annotated[UserVerifyServiceInterface, Depends()],
):
    await user_verify_service.verify(verify_token)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=None,
    )
