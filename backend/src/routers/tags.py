from typing import List

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from pydantic import parse_obj_as
from starlette import status
from starlette.responses import JSONResponse

from auth.auth import get_current_user_info
from dependencies.tags import get_tag_service
from schemas.posts import PostReadSchema, PostTagBaseSchema, PostTagReadSchema
from schemas.tags import TagCreateSchema, TagReadSchema, TagUpdateSchema
from services.tags import TagService

router = APIRouter(
    prefix='/api/v1/tags',
    tags=['Tags'],
)


@router.get('')
async def get_tags(
    tag_service: TagService = Depends(get_tag_service),
):
    data = await tag_service.get_tags()
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
    tag_service: TagService = Depends(get_tag_service),
    user_info: dict = Depends(get_current_user_info),
):
    data = await tag_service.create_tag(tag.dict(), user_info)
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
    tag_service: TagService = Depends(get_tag_service),
    user_info: dict = Depends(get_current_user_info),
):
    await tag_service.delete_tag(tag_id, user_info)
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content=None,
    )


@router.patch('/{tag_id}')
async def edit_tag(
    tag_id: int,
    update_data: TagUpdateSchema,
    tag_service: TagService = Depends(get_tag_service),
    user_info: dict = Depends(get_current_user_info),
):
    data = await tag_service.edit_tag(tag_id, update_data.dict(), user_info)
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
    tag_service: TagService = Depends(get_tag_service),
    user_info: dict = Depends(get_current_user_info),
):
    data = await tag_service.set_tag_on_post(post_id, data.dict(), user_info)
    data = jsonable_encoder(
        parse_obj_as(PostTagReadSchema, data),
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=data,
    )


@router.get('/{tag_id}/posts/')
async def get_posts_that_has_specify_tag(
    tag_id: int,
    tag_service: TagService = Depends(get_tag_service),
):
    data = await tag_service.get_posts_that_has_specify_tag(tag_id)
    data = jsonable_encoder(
        parse_obj_as(PostReadSchema, data),
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=data,
    )


@router.delete('/{tag_id}/posts/{post_id}')
async def delete_tag_on_post(
    tag_id: int,
    post_id: int,
    tag_service: TagService = Depends(get_tag_service),
    user_info: dict = Depends(get_current_user_info),
):
    await tag_service.delete_tag_on_post(tag_id, post_id, user_info)
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content=None,
    )
