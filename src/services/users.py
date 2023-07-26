from typing import List

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import parse_obj_as
from starlette import status

from auth.jwt import generate_jwt, decode_jwt
from config import SECRET_TOKEN_FOR_EMAIL, IS_TEST
from exceptions.base import NotFound
from exceptions.users import InvalidToken
from managers.users import UserManager
from models.users import User
from repositories.users import UserRepository
from schemas.users import UserReadBaseSchema, UserReadSchemaForAdmin
from tasks.users import send_verify_email


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def authenticate(
            self,
            email: str,
            input_password: str,
    ) -> int:
        user: User = await self.user_repo.get_info_for_authenticate(email)
        if not user or not UserManager.check_password(
                input_password=input_password,
                password_from_db=user.password,
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Credentials are not valid',
            )
        if not user.is_active or not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Account is not active',
            )
        return user.id

    async def get_users(
            self,
            user_info: dict,
    ) -> dict:
        fields = [User.id, User.email, User.username]
        if user_info.get('is_superuser'):
            fields += [User.registered_at, User.is_superuser, User.is_active, User.is_verified]

        data = await self.user_repo.get_all(fields=fields)
        schema = UserReadSchemaForAdmin if user_info.get('is_superuser') else UserReadBaseSchema
        data = parse_obj_as(List[schema], data)
        return jsonable_encoder(data)

    async def get_user(
            self,
            user_info: dict,
            user_id: int,
    ) -> dict:
        fields = [User.id, User.email, User.username]
        if user_info.get('is_superuser'):
            fields += [User.registered_at, User.is_superuser, User.is_active, User.is_verified]

        data = await self.user_repo.get_one(user_id, fields=fields)
        if not data:
            raise NotFound
        schema = UserReadSchemaForAdmin if user_info.get('is_superuser') else UserReadBaseSchema
        data = jsonable_encoder(parse_obj_as(schema, data))
        return data

    async def create_user(
            self,
            user_data: dict,
    ) -> dict:
        user_data.pop('password1')
        user = await self.user_repo.is_user_exists_by_email(user_data.get('email'))
        if user:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='User with this email already exists',
            )
        hashed_password = UserManager.make_password(user_data.pop('password2'))
        user_id = await self.user_repo.create(user_data, hashed_password)
        user_data.update({'id': user_id})
        self.after_create(user_data)
        return user_data

    def after_create(self, user_data: dict):
        verify_token = generate_jwt(
            data=user_data,
            lifetime_seconds=60 * 60 * 24 * 3,
            secret=SECRET_TOKEN_FOR_EMAIL,
        )

        """ FROM CONFIG, TO NOT SENDING EMAIL VERIFY WHEN TESTING """
        if IS_TEST:
            return

        send_verify_email.delay(user_data.get('email'), verify_token)

    async def verify(self, token: str) -> None:
        verify_token = decode_jwt(
            encoded_jwt=token,
            secret=SECRET_TOKEN_FOR_EMAIL,
        )
        email = verify_token.get('email')
        user = await self.user_repo.get_user_by_email(email)
        if user.id != verify_token.get('id'):
            raise InvalidToken
        if user.is_verified:
            raise InvalidToken
        await self.user_repo.update_user_verified_status(email)
