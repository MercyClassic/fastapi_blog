from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_async_session
from repositories.users import UserRepository
from services.users import UserService
from utils.utils import get_pagination_params


def get_user_service(
    session: AsyncSession = Depends(get_async_session),
    pagination_params: dict = Depends(get_pagination_params),
):
    return UserService(UserRepository(session, pagination_params))
