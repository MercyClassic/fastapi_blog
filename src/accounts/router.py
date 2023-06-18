from typing import List, Dict, Union
from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from pydantic import parse_obj_as
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only
from starlette import status
from starlette.responses import JSONResponse

from src.db.database import get_async_session

from src.accounts.schemas import (
    UserCreateSchema,
    UserReadBaseSchema,
    UserReadSchemaForAdmin
)
from src.accounts.auth import auth_backend
from src.accounts.manager import get_user_manager
from src.accounts.models import User

from fastapi_users import FastAPIUsers


router = APIRouter(
    prefix='/users',
    tags=['Accounts']
)


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend]
)

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/auth',
    tags=['Auth'],
)

router.include_router(
    fastapi_users.get_register_router(UserReadBaseSchema, UserCreateSchema),
    prefix='/auth',
    tags=['Auth'],
)


@router.get('/')
async def get_users(
        session: AsyncSession = Depends(get_async_session),
        # user: User = Depends(fastapi_users.current_user()),
) -> JSONResponse:
    query = select(User).where(User.is_active == True)
    result = await session.execute(query)
    # schema = UserReadSchemaForAdmin if user.is_superuser else UserReadBaseSchema
    schema = UserReadBaseSchema
    data = parse_obj_as(List[schema], result.scalars().all())
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(data)
    )


@router.get('/me/{user_id}')
async def get_me(
        session: AsyncSession = Depends(get_async_session),
        user_id: int = None,
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


@router.post('/register')
async def registration(
        user: UserCreateSchema,
        session: AsyncSession = Depends(get_async_session)
) -> JSONResponse:
    stmt = insert(User).values(**user.dict())
    user = await session.execute(stmt)
    await session.commit()
    data = parse_obj_as(UserReadBaseSchema, user)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder(data)
    )