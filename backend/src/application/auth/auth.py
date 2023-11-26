from fastapi import Depends

from application.managers.users import UserManager
from main.di.dependencies.jwt import get_access_token_from_headers


async def get_current_user_info(
    access_token: str = Depends(get_access_token_from_headers),
) -> dict:
    return UserManager.get_user_info_from_access_token(access_token)