from typing import List

from fastapi import Form, UploadFile
from pydantic import BaseModel, Field, validator

from schemas.base import CreatedAtBaseSchema
from schemas.tags import TagReadSchema
from schemas.users import UserReadBaseSchema
from utils.as_form import as_form
from utils.utils import get_stripped_value


class PostTagBaseSchema(BaseModel):
    tag_id: int

    class Config:
        orm_mode = True


class PostTagReadSchema(PostTagBaseSchema):
    id: int
    post_id: int


class PostBaseSchema(BaseModel):
    title: str = Field(min_length=1, max_length=50)
    content: str = Field(min_length=1, max_length=1000)
    published: bool

    @validator('title', 'content')
    def validate_title_and_content(cls, value):
        return get_stripped_value(value)

    class Config:
        orm_mode = True


@as_form
class PostCreateSchema(PostBaseSchema):
    image: UploadFile | None | str = Form(None)


@as_form
class PostUpdateSchema(PostBaseSchema):
    image: UploadFile | None | str = Form(None)


class PostReadBaseSchema(CreatedAtBaseSchema, PostBaseSchema):
    id: int
    image: str | None


class PostReadSchema(PostReadBaseSchema):
    user: UserReadBaseSchema
    tags: List[TagReadSchema] | list
