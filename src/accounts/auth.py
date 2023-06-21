from fastapi import Depends
from starlette import status
from starlette.exceptions import HTTPException
from starlette.requests import Request
from src.accounts.manager import UserManager


async def get_access_token_from_request(request: Request) -> str:
    """ USING FOR DEPENDENCY """
    return request.cookies.get('access_token')


async def get_current_user_info(
        access_token: str = Depends(get_access_token_from_request),
        without_exception: bool = False
) -> dict | None:
    user_info = UserManager.get_user_info_from_access_token(access_token, without_exception)
    if not user_info:
        if without_exception:
            return None
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    return user_info
