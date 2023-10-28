from typing import List, Annotated

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from pydantic import parse_obj_as
from starlette import status
from starlette.responses import JSONResponse

from auth.auth import get_current_user_info
from schemas.posts import (
    PostCreateSchema,
    PostReadBaseSchema,
    PostReadSchema,
    PostUpdateSchema,
)
from services.posts import PostServiceInterface
from uow import UnitOfWorkInterface

router = APIRouter(
    prefix='/api/v1/posts',
    tags=['Posts'],
)


@router.post('')
async def create_post(
    post: Annotated[PostCreateSchema, Depends(PostCreateSchema.as_form)],
    user_info: Annotated[dict, Depends(get_current_user_info)],
    post_service: Annotated[PostServiceInterface, Depends()],
    uow: Annotated[UnitOfWorkInterface, Depends()],
):
    data = await post_service.create_post(post.dict(), user_info, uow)
    data = jsonable_encoder(
        parse_obj_as(PostReadBaseSchema, data),
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=data,
    )


@router.get('/user/{user_id}')
async def get_user_posts(
    user_id: int,
    post_service: Annotated[PostServiceInterface, Depends()],
    uow: Annotated[UnitOfWorkInterface, Depends()],
):
    data = await post_service.get_user_posts(user_id, uow)
    data = jsonable_encoder(
        parse_obj_as(List[PostReadSchema], data),
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=data,
    )


@router.get('')
async def get_posts(
    post_service: Annotated[PostServiceInterface, Depends()],
    uow: Annotated[UnitOfWorkInterface, Depends()],
):
    data = await post_service.get_posts(uow)
    data = jsonable_encoder(
        parse_obj_as(List[PostReadSchema], data),
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=data,
    )


@router.get('/{post_id}')
async def get_post(
    post_id: int,
    post_service: Annotated[PostServiceInterface, Depends()],
    uow: Annotated[UnitOfWorkInterface, Depends()],
):
    data = await post_service.get_post(post_id, uow)
    data = jsonable_encoder(
        parse_obj_as(PostReadSchema, data),
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=data,
    )


@router.patch('/{post_id}')
async def edit_post(
    post_id: int,
    update_data: Annotated[PostUpdateSchema, Depends(PostUpdateSchema.as_form)],
    post_service: Annotated[PostServiceInterface, Depends()],
    uow: Annotated[UnitOfWorkInterface, Depends()],
    user_info: dict = Depends(get_current_user_info),
):
    data = await post_service.edit_post(
        post_id,
        update_data.dict(exclude_none=True),
        user_info,
        uow,
    )
    data = jsonable_encoder(
        parse_obj_as(PostReadBaseSchema, data),
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=data,
    )


@router.delete('/{post_id}')
async def delete_post(
    post_id: int,
    post_service: Annotated[PostServiceInterface, Depends()],
    uow: Annotated[UnitOfWorkInterface, Depends()],
    user_info: Annotated[dict, Depends(get_current_user_info)],
):
    await post_service.delete_post(post_id, user_info, uow)
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content=None,
    )
