from abc import ABC, abstractmethod


class UserServiceInterface(ABC):
    @abstractmethod
    async def authenticate(
        self,
        email: str,
        input_password: str,
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    async def get_users(
        self,
        user_info: dict,
    ):
        raise NotImplementedError

    @abstractmethod
    async def get_user(
        self,
        user_info: dict,
        user_id: int,
    ):
        raise NotImplementedError

    @abstractmethod
    async def create_user(
        self,
        user_data: dict,
    ) -> dict:
        raise NotImplementedError


class SendVerifyMessageServiceInterface(ABC):
    @abstractmethod
    def send_verify_message(
        self,
        user_data: dict,
    ):
        raise NotImplementedError


class UserVerifyServiceInterface(ABC):
    @abstractmethod
    async def verify(
        self,
        token: str,
    ) -> None:
        raise NotImplementedError
