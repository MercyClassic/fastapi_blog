from typing import List, Optional, Union

from fastapi import UploadFile
from pydantic import BaseModel, Field, validator

from application.models.tags import TagReadSchema
from application.models.users import UserReadBaseSchema
from application.utils.as_form import as_form
from application.utils.utils import get_stripped_value
from common.models.base import CreatedAtBaseSchema


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
        if value:
            return get_stripped_value(value)

    class Config:
        orm_mode = True


@as_form
class PostCreateSchema(PostBaseSchema):
    image: Union[UploadFile, str, None]


@as_form
class PostUpdateSchema(BaseModel):
    image: Union[UploadFile, str, None]
    title: Optional[str] = Field(min_length=1, max_length=50)
    content: Optional[str] = Field(min_length=1, max_length=1000)
    published: Optional[bool]

    @validator('title', 'content')
    def validate_title_and_content(cls, value):
        if value:
            return get_stripped_value(value)


class PostReadBaseSchema(CreatedAtBaseSchema, PostBaseSchema):
    id: int
    image: str | None


class PostReadSchema(PostReadBaseSchema):
    user: UserReadBaseSchema
    tags: List[TagReadSchema]
