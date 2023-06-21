from typing import List
from fastapi.encoders import jsonable_encoder
from pydantic import parse_obj_as
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only
from starlette import status
from starlette.responses import JSONResponse

from src.accounts.models import User
from src.accounts.schemas import UserReadSchemaForAdmin, UserReadBaseSchema


async def get_users(
        session: AsyncSession,
        user_info: dict
) -> JSONResponse:
    fields = [User.id, User.email, User.username]
    if user_info.get('is_superuser'):
        fields += [User.registered_at, User.is_superuser, User.is_active, User.is_verified]
    query = select(User).where(User.is_active == True).options(load_only(*fields))
    result = await session.execute(query)
    schema = UserReadSchemaForAdmin if user_info.get('is_superuser') else UserReadBaseSchema
    data = parse_obj_as(List[schema], result.scalars().all())
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(data)
    )


async def get_user(
        user_id: int,
        session: AsyncSession
) -> JSONResponse:
    query = select(User).where(User.id == user_id).options(load_only(User.id, User.username, User.email))
    result = await session.execute(query)
    result = result.scalar()
    if result is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=None
        )
    data = parse_obj_as(UserReadBaseSchema, result)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(data)
    )
