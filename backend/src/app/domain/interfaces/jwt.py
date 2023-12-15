from abc import ABC, abstractmethod


class JWTServiceInterface(ABC):
    @abstractmethod
    async def create_auth_tokens(
        self,
        user_id: int,
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
    ):
        raise NotImplementedError

    @abstractmethod
    async def delete_refresh_token(
        self,
        refresh_token: str,
    ):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    async def delete_user_tokens_if_not_exist(
        token: str,
        token_data: dict,
    ):
        raise NotImplementedError
