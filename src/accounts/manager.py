import hashlib
import os
import jwt
from pydantic.datetime_parse import datetime, timedelta
from sqlalchemy import insert, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only
from starlette import status
from starlette.exceptions import HTTPException

from src.accounts.models import User
from src.accounts.refresh_token_model import RefreshToken
from src.accounts.schemas import UserCreateSchema
from src.config import (
    JWT_SECRET_KEY,
    JWT_REFRESH_SECRET_KEY,
    ALGORITHM
)


class UserManager:
    @staticmethod
    async def authenticate(
            email: str,
            input_password: str,
            session: AsyncSession
    ) -> int | Exception:
        query = select(User).where(User.email == email).options(
            load_only(
                User.id, User.email, User.password, User.is_active
            ))
        result = await session.execute(query)
        user = result.scalar()
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
    async def create_jwt_tokens(user_id: int, session: AsyncSession) -> dict:
        return {
            'access_token': UserManager.create_access_token(user_id),
            'refresh_token': await UserManager.create_refresh_token(user_id, session)
        }

    @staticmethod
    def create_access_token(user_id: int) -> str:
        expires_delta = datetime.utcnow() + timedelta(minutes=60)
        to_encode = {"exp": expires_delta, "sub": str(user_id), "is_admin": True}
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
        return encoded_jwt

    @staticmethod
    async def create_refresh_token(user_id: int, session: AsyncSession) -> str:
        expires_delta = datetime.utcnow() + timedelta(minutes=60*24*7)
        to_encode = {"exp": expires_delta, "sub": str(user_id)}
        encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)

        stmt = insert(RefreshToken).values(user_id=user_id, token=encoded_jwt)
        await session.execute(stmt)
        await session.commit()

        return encoded_jwt

    @staticmethod
    def get_user_info_from_access_token(
            access_token: str, without_exception: bool = False
    ) -> dict | None:
        bad_status_code = None
        try:
            access_token_data = jwt.decode(access_token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.exceptions.ExpiredSignatureError:
            bad_status_code = 401
        except (
                jwt.exceptions.InvalidSignatureError,
                jwt.exceptions.DecodeError,
        ):
            bad_status_code = 403
        if bad_status_code:
            if without_exception:
                return None
            if bad_status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            elif bad_status_code == 403:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        return {
            'user_id': int(access_token_data.get('sub')),
            'is_admin': access_token_data.get('is_admin')
        }

    @staticmethod
    async def refresh_access_token(refresh_token: str, session: AsyncSession) -> dict:
        try:
            refresh_token_data = jwt.decode(refresh_token, JWT_REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.exceptions.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except (jwt.exceptions.InvalidSignatureError, jwt.exceptions.DecodeError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        ''' DELETE TOKEN AND RETURNING ID, IF ID IS NONE THAT MEAN ID WAS DELETED EARLY, MOST LIKELY BY HACKER '''
        stmt = delete(RefreshToken).where(RefreshToken.token == refresh_token).returning(RefreshToken.id)
        returned_id = await session.execute(stmt)
        await session.commit()
        check = [i for i in returned_id]
        if not check:
            await UserManager.delete_all_refresh_tokens(int(refresh_token_data.get('sub')), session)

        tokens = await UserManager.create_jwt_tokens(int(refresh_token_data.get('sub')), session)
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
        hashed_password = UserManager.make_password(user_data.pop('password2'))
        stmt = insert(User).values(
            **user_data,
            password=hashed_password
        ).returning(User.id)
        result = await session.execute(stmt)
        await session.commit()
        user_data.setdefault('id', result.one().id)
        UserManager.after_create(user_data.get('email'))
        return user_data

    @staticmethod
    def after_create(email: str) -> None:
        # here must be send email to verify (celery task)
        pass

    @staticmethod
    def make_password(value: str) -> str:
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
