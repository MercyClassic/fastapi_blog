from app.application.interfaces.encoders.jwt import JWTEncoderInterface
from app.domain.exceptions.base import NotFound
from app.domain.exceptions.users import (
    AccountAlreadyActivated,
    AccountIsNotActive,
    InvalidCredentials,
    InvalidToken,
    UserAlreadyExists,
)
from app.domain.interfaces.users import (
    SendVerifyMessageServiceInterface,
    UserServiceInterface,
    UserVerifyServiceInterface,
)
from app.domain.managers.users import UserManager
from app.domain.tasks.users import send_verify_email
from app.infrastructure.db.uow import UnitOfWorkInterface


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
            raise UserAlreadyExists
        hashed_password = UserManager.make_password(user_data.pop('password2'))
        user_id = await self.uow.user_repo.create_user(user_data, hashed_password)
        await self.uow.commit()
        user_data.update({'id': user_id})
        return user_data


class SendVerifyMessageService(SendVerifyMessageServiceInterface):
    def __init__(
        self,
        jwt_encoder: JWTEncoderInterface,
        secret_token_for_email: str,
    ):
        self.jwt_encoder = jwt_encoder
        self.secret_token_for_email = secret_token_for_email

    def send_verify_message(
        self,
        user_data: dict,
    ):
        verify_token = self.jwt_encoder.generate_jwt(
            data=user_data,
            lifetime_seconds=60 * 60 * 24 * 3,
            secret=self.secret_token_for_email,
        )

        send_verify_email.delay(user_data.get('email'), verify_token)


class UserVerifyService(UserVerifyServiceInterface):
    def __init__(
        self,
        uow: UnitOfWorkInterface,
        jwt_encoder: JWTEncoderInterface,
        secret_token_for_email: str,
    ):
        self.uow = uow
        self.jwt_encoder = jwt_encoder
        self.secret_token_for_email = secret_token_for_email

    async def verify(
        self,
        token: str,
    ) -> None:
        verify_data = self.jwt_encoder.decode_jwt(
            encoded_jwt=token,
            secret=self.secret_token_for_email,
        )
        email = verify_data.get('email')
        user = await self.uow.user_repo.get_user_by_email(email)
        if user.id != verify_data.get('id'):
            raise InvalidToken
        if user.is_verified:
            raise AccountAlreadyActivated
        await self.uow.user_repo.update_user_verified_status(email)
        await self.uow.commit()
