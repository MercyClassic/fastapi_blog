from fastapi import Depends
from starlette.requests import Request
from src.managers.users import UserManager


async def get_access_token_from_request(request: Request) -> str:
    """ USING FOR DEPENDENCY """
    return request.headers.get('Authorization')


async def get_current_user_info(
        access_token: str = Depends(get_access_token_from_request)
) -> dict:
    return UserManager.get_user_info_from_access_token(access_token)
