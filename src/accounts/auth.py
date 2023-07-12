from fastapi import Depends
from starlette.requests import Request
from src.accounts.manager import UserManager


async def get_access_token_from_request(request: Request) -> str:
    """ USING FOR DEPENDENCY """
    return request.cookies.get('access_token')


async def get_current_user_info(
        access_token: str = Depends(get_access_token_from_request)
) -> dict:
    return UserManager.get_user_info_from_access_token(access_token)
