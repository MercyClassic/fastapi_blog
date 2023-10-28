from typing import List, Annotated

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from pydantic import parse_obj_as
from starlette import status
from starlette.responses import JSONResponse

from auth.auth import get_current_user_info
from schemas.posts import PostTagBaseSchema, PostTagReadSchema
from schemas.tags import TagCreateSchema, TagReadSchema, TagUpdateSchema
from services.tags import TagServiceInterface
from uow import UnitOfWorkInterface

router = APIRouter(
    prefix='/api/v1/tags',
    tags=['Tags'],
)


@router.get('')
async def get_tags(
    tag_service: Annotated[TagServiceInterface, Depends()],
    uow: Annotated[UnitOfWorkInterface, Depends()],
):
    data = await tag_service.get_tags(uow)
    data = jsonable_encoder(
        parse_obj_as(List[TagReadSchema], data),
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=data,
    )


@router.post('')
async def create_tag(
    tag: TagCreateSchema,
    tag_service: Annotated[TagServiceInterface, Depends()],
    user_info: Annotated[dict, Depends(get_current_user_info)],
    uow: Annotated[UnitOfWorkInterface, Depends()],
):
    data = await tag_service.create_tag(tag.dict(), user_info, uow)
    data = jsonable_encoder(
        parse_obj_as(TagReadSchema, data),
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=data,
    )


@router.delete('/{tag_id}')
async def delete_tag(
    tag_id: int,
    tag_service: Annotated[TagServiceInterface, Depends()],
    user_info: Annotated[dict, Depends(get_current_user_info)],
    uow: Annotated[UnitOfWorkInterface, Depends()],
):
    await tag_service.delete_tag(tag_id, user_info, uow)
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content=None,
    )


@router.patch('/{tag_id}')
async def edit_tag(
    tag_id: int,
    update_data: TagUpdateSchema,
    tag_service: Annotated[TagServiceInterface, Depends()],
    user_info: Annotated[dict, Depends(get_current_user_info)],
    uow: Annotated[UnitOfWorkInterface, Depends()],
):
    data = await tag_service.edit_tag(
        tag_id,
        update_data.dict(),
        user_info,
        uow,
    )
    data = jsonable_encoder(
        parse_obj_as(TagReadSchema, data),
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=data,
    )


@router.post('/post/{post_id}')
async def set_tag_on_post(
    post_id: int,
    data: PostTagBaseSchema,
    tag_service: Annotated[TagServiceInterface, Depends()],
    user_info: Annotated[dict, Depends(get_current_user_info)],
    uow: Annotated[UnitOfWorkInterface, Depends()],
):
    data = await tag_service.set_tag_on_post(
        post_id,
        data.dict(),
        user_info,
        uow,
    )
    data = jsonable_encoder(
        parse_obj_as(PostTagReadSchema, data),
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=data,
    )


@router.delete('/{tag_id}/posts/{post_id}')
async def delete_tag_on_post(
    tag_id: int,
    post_id: int,
    tag_service: Annotated[TagServiceInterface, Depends()],
    user_info: Annotated[dict, Depends(get_current_user_info)],
    uow: Annotated[UnitOfWorkInterface, Depends()],
):
    await tag_service.delete_tag_on_post(
        tag_id,
        post_id,
        user_info,
        uow,
    )
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content=None,
    )
