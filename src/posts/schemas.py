from typing import List

from fastapi import UploadFile, Form
from pydantic import BaseModel, validator
from pydantic import Field
from src.accounts.schemas import UserReadBaseSchema
from src.utils.as_form import as_form


class CreatedAtBaseSchema(BaseModel):
    created_at: str

    @validator('created_at', pre=True)
    def parse_created_at(cls, v):
        return v.strftime('%Y-%m-%d %H:%M:%S')


class PostTagBaseSchema(BaseModel):
    tag_id: int
    post_id: int

    class Config:
        orm_mode = True


class PostTagReadSchema(PostTagBaseSchema):
    id: int


class TagBaseSchema(BaseModel):
    name: str

    class Config:
        orm_mode = True


class TagCreateSchema(TagBaseSchema):
    pass


class TagUpdateSchema(TagBaseSchema):
    pass


class TagReadSchema(CreatedAtBaseSchema, TagBaseSchema):
    id: int


class PostBaseSchema(BaseModel):
    title: str = Field(max_length=50)
    content: str
    published: bool

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
