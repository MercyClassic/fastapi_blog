from typing import List

from fastapi import Form, UploadFile
from pydantic import BaseModel, Field, validator

from schemas.users import UserReadBaseSchema
from utils.as_form import as_form
from utils.utils import get_stripped_value


class CreatedAtBaseSchema(BaseModel):
    created_at: str

    @validator('created_at', pre=True)
    def parse_created_at(cls, value):
        return value.strftime('%Y-%m-%d %H:%M:%S')


class PostTagBaseSchema(BaseModel):
    tag_id: int

    class Config:
        orm_mode = True


class PostTagReadSchema(PostTagBaseSchema):
    id: int
    post_id: int


class TagBaseSchema(BaseModel):
    name: str = Field(min_length=1, max_length=50)

    @validator('name')
    def validate_name(cls, value):
        return get_stripped_value(value)

    class Config:
        orm_mode = True


class TagCreateSchema(TagBaseSchema):
    pass


class TagUpdateSchema(TagBaseSchema):
    pass


class TagReadSchema(CreatedAtBaseSchema, TagBaseSchema):
    id: int


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
