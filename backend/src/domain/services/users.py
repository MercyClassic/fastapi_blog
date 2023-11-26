from fastapi import HTTPException
from starlette import status

from application.auth.jwt import decode_jwt, generate_jwt
from application.managers.users import UserManager
from common.exceptions.base import NotFound
from domain.exceptions.users import (
    AccountAlreadyActivated,
    AccountIsNotActive,
    InvalidCredentials,
    InvalidToken,
)
from domain.interfaces.users import UserServiceInterface
from domain.tasks.users import send_verify_email
from infrastructure.db.uow import UnitOfWorkInterface
from main.config import get_settings


class UserService(UserServiceInterface):
    def __init__(
        self,
        uow: UnitOfWorkInterface,
    ):
        self.uow = uow

    async def authenticate(
        self,
        email: str,
        input_password: str,
    ) -> int:
        user = await self.uow.user_repo.get_info_for_authenticate(email)
        if not user or not UserManager.check_password(
            input_password=input_password,
            password_from_db=user.password,
        ):
            raise InvalidCredentials
        if not user.is_active or not user.is_verified:
            raise AccountIsNotActive
        return user.id

    async def get_users(
        self,
        user_info: dict,
    ):
        data = await self.uow.user_repo.get_users(
            is_superuser=bool(user_info.get('is_superuser')),
        )
        return data

    async def get_user(
        self,
        user_info: dict,
        user_id: int,
    ):
        data = await self.uow.user_repo.get_user(
            user_id,
            is_superuser=bool(user_info.get('is_superuser')),
        )
        if not data:
            raise NotFound
        return data

    async def create_user(
        self,
        user_data: dict,
    ) -> dict:
        user_data.pop('password1')
        user = await self.uow.user_repo.is_user_exists_by_email(user_data.get('email'))
        if user:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='User with this email already exists',
            )
        hashed_password = UserManager.make_password(user_data.pop('password2'))
        user_id = await self.uow.user_repo.create_user(user_data, hashed_password)
        await self.uow.commit()
        user_data.update({'id': user_id})
        self.after_create(user_data)
        return user_data

    @staticmethod
    def after_create(
        user_data: dict,
    ):
        verify_token = generate_jwt(
            data=user_data,
            lifetime_seconds=60 * 60 * 24 * 3,
            secret=get_settings().SECRET_TOKEN_FOR_EMAIL,
        )

        send_verify_email.delay(user_data.get('email'), verify_token)

    async def verify(
        self,
        token: str,
    ) -> None:
        verify_token = decode_jwt(
            encoded_jwt=token,
            secret=get_settings().SECRET_TOKEN_FOR_EMAIL,
        )
        email = verify_token.get('email')
        user = await self.uow.user_repo.get_user_by_email(email)
        if user.id != verify_token.get('id'):
            raise InvalidToken
        if user.is_verified:
            raise AccountAlreadyActivated
        await self.uow.user_repo.update_user_verified_status(email)
        await self.uow.commit()
