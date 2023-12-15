from abc import ABC, abstractmethod

from app.infrastructure.db.repositories.jwt import JWTRepository
from app.infrastructure.db.repositories.posts import PostRepository
from app.infrastructure.db.repositories.tags import TagRepository
from app.infrastructure.db.repositories.users import UserRepository


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
