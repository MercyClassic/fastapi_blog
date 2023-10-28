from abc import ABC, abstractmethod

from auth.jwt import decode_jwt, generate_jwt
from uow.uow import UnitOfWorkInterface


class JWTServiceInterface(ABC):
    @abstractmethod
    async def create_auth_tokens(
            self,
            user_id: int,
            uow: UnitOfWorkInterface,
    ):
        raise NotImplementedError

    @abstractmethod
    async def create_refresh_token(
            self,
            user_id: int,
    ):
        raise NotImplementedError

    @abstractmethod
    async def create_access_token(
            self,
            user_id: int,
            is_superuser: bool,
    ):
        raise NotImplementedError

    @abstractmethod
    async def refresh_auth_tokens(
            self,
            refresh_token: str,
            uow: UnitOfWorkInterface,
    ):
        raise NotImplementedError

    @abstractmethod
    async def delete_refresh_token(
            self,
            refresh_token: str,
            uow: UnitOfWorkInterface,
    ):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    async def delete_user_tokens_if_not_exist(
            token: str,
            token_data: dict,
            uow: UnitOfWorkInterface,
    ):
        raise NotImplementedError


class JWTService(JWTServiceInterface):
    def __init__(
            self,
            jwt_access_key: str,
            jwt_refresh_key: str,
    ):
        self.jwt_access_key = jwt_access_key
        self.jwt_refresh_key = jwt_refresh_key

    async def create_auth_tokens(
            self,
            user_id: int,
            uow: UnitOfWorkInterface,
    ):
        async with uow:
            is_superuser = await uow.jwt_repo.is_superuser(user_id)

            access_token = await self.create_access_token(user_id, is_superuser)
            refresh_token = await self.create_refresh_token(user_id)

            await uow.jwt_repo.save_refresh_token(user_id, refresh_token)
            await uow.commit()

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
        }

    async def create_refresh_token(
            self,
            user_id: int,
    ) -> str:
        to_encode = {'sub': str(user_id)}
        encoded_jwt = generate_jwt(
            data=to_encode,
            lifetime_seconds=60 * 60 * 24 * 7,
            secret=self.jwt_refresh_key,
        )
        return encoded_jwt

    async def create_access_token(
            self,
            user_id: int,
            is_superuser: bool,
    ) -> str:
        to_encode = {'sub': str(user_id), 'is_superuser': is_superuser}
        return generate_jwt(
            data=to_encode,
            lifetime_seconds=60 * 60,
            secret=self.jwt_access_key,
        )

    async def refresh_auth_tokens(
            self,
            refresh_token: str,
            uow: UnitOfWorkInterface,
    ):
        refresh_token_data = decode_jwt(
            encoded_jwt=refresh_token,
            secret=self.jwt_refresh_key,
        )
        async with uow:
            await self.delete_user_tokens_if_not_exist(refresh_token, refresh_token_data, uow)
            await uow.commit()

        tokens = await self.create_auth_tokens(int(refresh_token_data.get('sub')), uow)

        return tokens

    async def delete_refresh_token(
            self,
            refresh_token: str,
            uow: UnitOfWorkInterface,
    ) -> None:
        refresh_token_data = decode_jwt(
            encoded_jwt=refresh_token,
            secret=self.jwt_refresh_key,
            soft=True,
        )
        async with uow:
            await self.delete_user_tokens_if_not_exist(refresh_token, refresh_token_data, uow)
            await uow.commit()

    @staticmethod
    async def delete_user_tokens_if_not_exist(
            token: str,
            token_data: dict,
            uow: UnitOfWorkInterface,
    ) -> None:
        deleted_id = await uow.jwt_repo.delete_refresh_token(token)
        """
        DELETE TOKEN AND RETURNING ID
        IF ID IS NONE THAT MEANS ID WAS DELETED EARLY, MOST LIKELY BY HACKER
        """
        if not deleted_id:
            await uow.jwt_repo.delete_all_user_refresh_tokens(int(token_data.get('sub')))
