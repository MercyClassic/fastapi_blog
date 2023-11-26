from abc import ABC, abstractmethod

from infrastructure.db.repositories.jwt import JWTRepository
from infrastructure.db.repositories.posts import PostRepository
from infrastructure.db.repositories.tags import TagRepository
from infrastructure.db.repositories.users import UserRepository


class UnitOfWorkInterface(ABC):
    user_repo: UserRepository
    post_repo: PostRepository
    tag_repo: TagRepository
    jwt_repo: JWTRepository

    @abstractmethod
    async def commit(self):
        raise NotImplementedError

    @abstractmethod
    async def rollback(self):
        raise NotImplementedError
