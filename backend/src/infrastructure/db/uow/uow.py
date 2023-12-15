from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.interfaces.repositories.uow import UnitOfWorkInterface
from infrastructure.db.repositories.jwt import JWTRepository
from infrastructure.db.repositories.posts import PostRepository
from infrastructure.db.repositories.tags import TagRepository
from infrastructure.db.repositories.users import UserRepository


class UnitOfWork(UnitOfWorkInterface):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(self.session)
        self.post_repo = PostRepository(self.session)
        self.tag_repo = TagRepository(self.session)
        self.jwt_repo = JWTRepository(self.session)

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
