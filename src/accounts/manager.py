import hashlib
import os
from sqlalchemy import insert, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only
from starlette import status
from starlette.exceptions import HTTPException
from src.accounts.exceptions import InvalidToken
from src.accounts.models import User, RefreshToken
from src.accounts.jwt import generate_jwt, decode_jwt
from src.accounts.schemas import UserCreateSchema
from src.accounts.tasks import send_verify_email
from src.config import (
    JWT_SECRET_KEY,
    JWT_REFRESH_SECRET_KEY,
    SECRET_TOKEN_FOR_EMAIL,
    IS_TEST
)


class UserManager:
    @staticmethod
    async def authenticate(
            email: str,
            input_password: str,
            session: AsyncSession
    ) -> int:
        query = select(User).where(User.email == email).options(
            load_only(
                User.id, User.email, User.password, User.is_active
            ))
        result = await session.execute(query)
        user = result.scalar()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Credentials are not valid'
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Account is not verified'
            )
        if user is not None and UserManager.check_password(
            input_password=input_password, password_from_db=user.password
        ):
            return user.id
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Credentials are not valid'
        )

    @staticmethod
    async def create_auth_tokens(user_id: int, session: AsyncSession) -> dict:
        return {
            'access_token': await UserManager.create_access_token(user_id, session),
            'refresh_token': await UserManager.create_refresh_token(user_id, session)
        }

    @staticmethod
    async def create_access_token(user_id: int, session: AsyncSession) -> str:
        query = select(User).where(User.id == user_id).options(load_only(User.is_superuser))
        result = await session.execute(query)
        is_superuser = result.scalar().is_superuser
        to_encode = {"sub": str(user_id), 'is_superuser': is_superuser}
        return generate_jwt(
            data=to_encode,
            lifetime_seconds=60*60,
            secret=JWT_SECRET_KEY
        )

    @staticmethod
    async def create_refresh_token(user_id: int, session: AsyncSession) -> str:
        to_encode = {"sub": str(user_id)}
        encoded_jwt = generate_jwt(
            data=to_encode,
            lifetime_seconds=60*60*24*7,
            secret=JWT_REFRESH_SECRET_KEY
        )
        stmt = insert(RefreshToken).values(user_id=user_id, token=encoded_jwt)
        await session.execute(stmt)
        await session.commit()

        return encoded_jwt

    @staticmethod
    def get_user_info_from_access_token(access_token: str) -> dict:
        access_token_data = decode_jwt(
            encoded_jwt=access_token,
            secret=JWT_SECRET_KEY
        )
        return {
            'user_id': int(access_token_data.get('sub')),
            'is_superuser': access_token_data.get('is_superuser')
        }

    @staticmethod
    async def refresh_access_token(refresh_token: str, session: AsyncSession) -> dict:
        refresh_token_data = decode_jwt(
            encoded_jwt=refresh_token,
            secret=JWT_REFRESH_SECRET_KEY
        )
        ''' DELETE TOKEN AND RETURNING ID, IF ID IS NONE THAT MEANS ID WAS DELETED EARLY, MOST LIKELY BY HACKER '''
        stmt = delete(RefreshToken).where(RefreshToken.token == refresh_token).returning(RefreshToken.id)
        returned_id = await session.execute(stmt)
        await session.commit()
        check = [i for i in returned_id]
        if not check:
            await UserManager.delete_all_refresh_tokens(int(refresh_token_data.get('sub')), session)

        tokens = await UserManager.create_auth_tokens(int(refresh_token_data.get('sub')), session)
        return tokens

    @staticmethod
    async def delete_all_refresh_tokens(user_id: int, session: AsyncSession) -> None:
        stmt = delete(RefreshToken).where(RefreshToken.user_id == user_id)
        await session.execute(stmt)
        await session.commit()

    @staticmethod
    async def delete_current_refresh_token(token: str, session: AsyncSession) -> None:
        stmt = delete(RefreshToken).where(RefreshToken.token == token)
        await session.execute(stmt)
        await session.commit()

    @staticmethod
    async def create_user(
            user_input_data: UserCreateSchema,
            session: AsyncSession
    ) -> dict:
        user_data = user_input_data.dict()
        user_data.pop('password1')
        query = select(1).where(User.email == user_data.get('email'))
        result = await session.execute(query)
        if result.scalar():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='User with this email already exists'
            )
        hashed_password = UserManager.make_password(user_data.pop('password2'))
        stmt = insert(User).values(
            **user_data,
            password=hashed_password
        ).returning(User.id)
        result = await session.execute(stmt)
        await session.commit()
        user_data.setdefault('id', result.one().id)
        UserManager.after_create(user_data)
        return user_data

    @staticmethod
    def after_create(user_data: dict) -> None:
        verify_token = generate_jwt(
            data=user_data,
            lifetime_seconds=60*60*24*3,
            secret=SECRET_TOKEN_FOR_EMAIL
        )

        """ FROM CONFIG """
        if IS_TEST:
            return

        send_verify_email.delay(user_data.get('email'), verify_token)

    @staticmethod
    async def get_user_by_email(email: str, session: AsyncSession) -> User:
        query = (
            select(User)
            .where(User.email == email)
            .options(load_only(User.id, User.email, User.is_verified))
        )
        result = await session.execute(query)
        user = result.scalar()
        return user

    @staticmethod
    async def verify(token: str, session: AsyncSession) -> None:
        verify_token = decode_jwt(
            encoded_jwt=token,
            secret=SECRET_TOKEN_FOR_EMAIL
        )
        email = verify_token.get('email')
        user = await UserManager.get_user_by_email(email, session)
        if user.id != verify_token.get('id'):
            raise InvalidToken
        if user.is_verified:
            raise InvalidToken
        stmt = update(User).values(is_verified=True).where(User.email == email)
        await session.execute(stmt)
        await session.commit()

    @staticmethod
    def make_password(value: str) -> str:
        if len(value) < 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Length password must be >= 4'
            )
        salt = os.urandom(32)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            value.encode('utf-8'),
            salt,
            100000
        )
        """ first 64 characters is password, last 64 is salt """
        hashed_password = '%s%s' % (password_hash.hex(), salt.hex())
        return hashed_password

    @staticmethod
    def check_password(*, input_password: str, password_from_db: str) -> bool:
        salt_from_db = bytes.fromhex(password_from_db[-64:])
        user_input_password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            input_password.encode('utf-8'),
            salt_from_db,
            100000
        )
        user_input_full_hashed_password = '%s%s' % (user_input_password_hash.hex(), salt_from_db.hex())
        if user_input_full_hashed_password == password_from_db:
            return True
        return False
