from datetime import datetime
from fastapi_users import schemas
from pydantic import EmailStr, BaseModel


class UserCreateSchema(schemas.BaseUserCreate):
    username: str
    email: EmailStr
    password: str

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
