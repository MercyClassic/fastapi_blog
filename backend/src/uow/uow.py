from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from repositories.users import UserRepository
from repositories.posts import PostRepository
from repositories.tags import TagRepository
from repositories.jwt import JWTRepository


class UnitOfWorkInterface(ABC):
    user_repo: UserRepository
    post_repo: PostRepository
    tag_repo: TagRepository
    jwt_repo: JWTRepository

    @abstractmethod
    async def __aenter__(self):
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    @abstractmethod
    async def commit(self):
        raise NotImplementedError

    @abstractmethod
    async def rollback(self):
        raise NotImplementedError


class UnitOfWork(UnitOfWorkInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self):
        self.user_repo = UserRepository(self.session)
        self.post_repo = PostRepository(self.session)
        self.tag_repo = TagRepository(self.session)
        self.jwt_repo = JWTRepository(self.session)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
