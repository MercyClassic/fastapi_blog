from abc import ABC, abstractmethod
from typing import List

from common.interfaces.db.sqlalchemy_gateway import SQLAlchemyBaseGateway
from infrastructure.db.models.posts import Post
from infrastructure.db.models.tags import PostTag, Tag


class TagRepositoryInterface(SQLAlchemyBaseGateway, ABC):
    @abstractmethod
    async def return_author_id(self, tag_id: int) -> Tag:
        raise NotImplementedError

    @abstractmethod
    async def get_tags(self) -> List[Tag]:
        raise NotImplementedError

    @abstractmethod
    async def create_tag(self, data: dict) -> Tag:
        raise NotImplementedError

    @abstractmethod
    async def update_tag(self, tag_id: int, update_data: dict) -> Tag:
        raise NotImplementedError

    @abstractmethod
    async def delete_tag(self, tag_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_post_tags(self, post_id: int) -> List[Tag]:
        raise NotImplementedError

    @abstractmethod
    async def set_tag_on_post(self, post_tag_data: dict) -> PostTag:
        raise NotImplementedError

    @abstractmethod
    async def get_post_tag_id(self, tag_id: int, post_id: int) -> int:
        raise NotImplementedError

    @abstractmethod
    async def delete_tag_on_post(self, post_tag_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def check_post_author(self, post_tag_id: int) -> Post:
        raise NotImplementedError
