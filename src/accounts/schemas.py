from datetime import datetime
from fastapi import HTTPException
from pydantic import EmailStr, BaseModel, validator
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
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Password is invalid'
            )
        return value

    class Config:
        orm_mode = True


class UserReadBaseSchema(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True


class UserReadSchemaForAdmin(UserReadBaseSchema):
    registered_at: datetime
    is_superuser: bool
    is_verified: bool
    is_active: bool


class AuthenticateSchema(BaseModel):
    email: EmailStr
    input_password: str