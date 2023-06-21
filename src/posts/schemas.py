from pydantic import BaseModel, validator
from pydantic import Field


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


class PostReadSchema(PostBaseSchema):
    id: int
    user_id: int
    created_at: str

    @validator('created_at', pre=True)
    def parse_created_at(cls, v):
        return v.strftime('%Y-%m-%d %H:%M:%S')


class TagBaseSchema(BaseModel):
    name: str


class TagCreateSchema(TagBaseSchema):
    pass


class TagReadSchema(TagBaseSchema):
    id: int
    created_at: str

    @validator('created_at', pre=True)
    def parse_created_at(cls, v):
        return v.strftime('%Y-%m-%d %H:%M:%S')