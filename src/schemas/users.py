from datetime import datetime

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, validator
from starlette import status


class UserCreateSchema(BaseModel):
    username: str
    email: EmailStr
    password1: str
    password2: str

    @validator('password2')
    def validate_password(cls, value, values):
        valid_characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!#@$_'
        if (
                value != values.get('password1')
                or any(i for i in value if i not in valid_characters)
                or len(value) < 4
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Password is invalid',
            )
        return value

    class Config:
        orm_mode = True


class UserReadBaseSchema(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True


class UserReadSchemaForAdmin(UserReadBaseSchema):
    email: EmailStr
    registered_at: datetime
    is_superuser: bool
    is_verified: bool
    is_active: bool
