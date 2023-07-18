from fastapi import Depends
from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only
from starlette.requests import Request

from auth.jwt import decode_jwt, generate_jwt
from config import JWT_REFRESH_SECRET_KEY, JWT_SECRET_KEY
from managers.users import UserManager
from models.users import RefreshToken, User


async def get_access_token_from_request(request: Request) -> str:
    """ USING FOR DEPENDENCY """
    return request.headers.get('Authorization')


async def get_current_user_info(
        access_token: str = Depends(get_access_token_from_request),
) -> dict:
    return UserManager.get_user_info_from_access_token(access_token)


async def create_auth_tokens(user_id: int, session: AsyncSession) -> dict:
    return {
        'access_token': await create_access_token(user_id, session),
        'refresh_token': await create_refresh_token(user_id, session),
    }


async def create_access_token(user_id: int, session: AsyncSession) -> str:
    query = select(User).where(User.id == user_id).options(load_only(User.is_superuser))
    result = await session.execute(query)
    is_superuser = result.scalar().is_superuser
    to_encode = {'sub': str(user_id), 'is_superuser': is_superuser}
    return generate_jwt(
        data=to_encode,
        lifetime_seconds=60 * 60,
        secret=JWT_SECRET_KEY,
    )


async def create_refresh_token(user_id: int, session: AsyncSession) -> str:
    to_encode = {'sub': str(user_id)}
    encoded_jwt = generate_jwt(
        data=to_encode,
        lifetime_seconds=60 * 60 * 24 * 7,
        secret=JWT_REFRESH_SECRET_KEY,
    )
    stmt = insert(RefreshToken).values(user_id=user_id, token=encoded_jwt)
    await session.execute(stmt)
    await session.commit()

    return encoded_jwt


async def refresh_tokens(refresh_token: str, session: AsyncSession) -> dict:
    refresh_token_data = decode_jwt(
        encoded_jwt=refresh_token,
        secret=JWT_REFRESH_SECRET_KEY,
    )
    """
    DELETE TOKEN AND RETURNING ID
    IF ID IS NONE THAT MEANS ID WAS DELETED EARLY, MOST LIKELY BY HACKER
    """
    stmt = (
        delete(RefreshToken)
        .where(RefreshToken.token == refresh_token)
        .returning(RefreshToken.id)
    )
    result = await session.execute(stmt)
    await session.commit()
    if not result.scalar():
        await delete_all_refresh_tokens(int(refresh_token_data.get('sub')), session)

    tokens = await create_auth_tokens(int(refresh_token_data.get('sub')), session)
    return tokens


async def delete_all_refresh_tokens(user_id: int, session: AsyncSession) -> None:
    stmt = delete(RefreshToken).where(RefreshToken.user_id == user_id)
    await session.execute(stmt)
    await session.commit()


async def delete_current_refresh_token(token: str, session: AsyncSession) -> None:
    token_data = decode_jwt(token, secret=JWT_REFRESH_SECRET_KEY)
    stmt = delete(RefreshToken).where(RefreshToken.token == token).returning(RefreshToken.id)
    result = await session.execute(stmt)
    await session.commit()
    if not result.scalar():
        await delete_all_refresh_tokens(int(token_data.get('sub')), session)
