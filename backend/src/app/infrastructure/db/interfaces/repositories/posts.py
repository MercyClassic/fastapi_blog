from abc import ABC, abstractmethod
from typing import List

from app.infrastructure.db.interfaces.repositories.sqlalchemy_gateway import (
    SQLAlchemyBaseGateway,
)
from app.infrastructure.db.models.posts import Post


class PostRepositoryInterface(SQLAlchemyBaseGateway, ABC):
    @abstractmethod
    async def return_author_id(self, post_id: int):
        raise NotImplementedError

    @abstractmethod
    async def get_user_posts(self, user_id: int) -> List[Post]:
        raise NotImplementedError

    @abstractmethod
    async def get_posts(self) -> List[Post]:
        raise NotImplementedError

    @abstractmethod
    async def get_post(self, post_id: int) -> Post:
        raise NotImplementedError

    @abstractmethod
    async def create_post(self, data: dict) -> Post:
        raise NotImplementedError

    @abstractmethod
    async def update_post(self, post_id: int, update_data: dict) -> Post:
        raise NotImplementedError

    @abstractmethod
    async def delete_post(self, post_id: int) -> None:
        raise NotImplementedError
