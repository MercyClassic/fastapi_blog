from abc import ABC, abstractmethod

from common.interfaces.db.sqlalchemy_gateway import SQLAlchemyBaseGateway


class JWTRepositoryInterface(SQLAlchemyBaseGateway, ABC):
    @abstractmethod
    async def is_superuser(self, user_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def save_refresh_token(self, user_id: int, token: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_refresh_token(self, token: str) -> int | None:
        raise NotImplementedError

    @abstractmethod
    async def delete_all_user_refresh_tokens(self, user_id: int) -> None:
        raise NotImplementedError
