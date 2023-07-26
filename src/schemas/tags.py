from pydantic import BaseModel, Field, validator

from schemas.base import CreatedAtBaseSchema
from utils.utils import get_stripped_value


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