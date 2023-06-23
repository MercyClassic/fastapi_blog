from typing import List
from pydantic import BaseModel, validator
from pydantic import Field
from src.accounts.schemas import UserReadBaseSchema


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
    image: str | None
    published: bool

    class Config:
        orm_mode = True


class PostCreateSchema(PostBaseSchema):
    pass


class PostUpdateSchema(PostBaseSchema):
    pass


class PostReadBaseSchema(CreatedAtBaseSchema, PostBaseSchema):
    id: int


class PostReadSchema(PostReadBaseSchema):
    user: UserReadBaseSchema
    tags: List[TagReadSchema] | list
