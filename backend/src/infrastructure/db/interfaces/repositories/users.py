from abc import ABC, abstractmethod
from typing import List

from common.interfaces.db.sqlalchemy_gateway import SQLAlchemyBaseGateway
from infrastructure.db.models.users import User


class UserRepositoryInterface(SQLAlchemyBaseGateway, ABC):
    @abstractmethod
    async def get_info_for_authenticate(self, email: str) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get_users(self, is_superuser: bool = False) -> List[User]:
        raise NotImplementedError

    @abstractmethod
    async def get_user(
        self,
        user_id: int,
        is_superuser: bool = False,
    ) -> User:
        raise NotImplementedError

    @abstractmethod
    async def create_user(
        self,
        user_data: dict,
        hashed_password: str,
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    async def is_user_exists_by_email(self, email: str) -> int | None:
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_email(self, email: str) -> User:
        raise NotImplementedError

    @abstractmethod
    async def update_user_verified_status(self, email: str) -> None:
        raise NotImplementedError
