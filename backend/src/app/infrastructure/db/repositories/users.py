from typing import List

from sqlalchemy import insert, select, update
from sqlalchemy.orm import load_only

from app.infrastructure.db.interfaces.repositories.users import UserRepositoryInterface
from app.infrastructure.db.models.users import User


class UserRepository(UserRepositoryInterface):
    async def get_info_for_authenticate(self, email: str) -> User:
        query = (
            select(User)
            .where(User.email == email)
            .options(
                load_only(
                    User.id,
                    User.email,
                    User.password,
                    User.is_active,
                    User.is_verified,
                ),
            )
        )
        result = await self.session.execute(query)
        return result.scalar()

    async def get_users(self, is_superuser: bool = False) -> List[User]:
        fields = [User.id, User.email, User.username]
        if is_superuser:
            fields += [User.registered_at, User.is_superuser, User.is_active, User.is_verified]
        query = select(User).where(User.is_active.is_(True)).options(load_only(*fields))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_user(
        self,
        user_id: int,
        is_superuser: bool = False,
    ) -> User:
        fields = [User.id, User.email, User.username]
        if is_superuser:
            fields += [User.registered_at, User.is_superuser, User.is_active, User.is_verified]
        query = select(User).where(User.id == user_id).options(load_only(*fields))
        result = await self.session.execute(query)
        return result.scalar()

    async def create_user(
        self,
        user_data: dict,
        hashed_password: str,
    ) -> int:
        stmt = insert(User).values(**user_data, password=hashed_password).returning(User.id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def is_user_exists_by_email(self, email: str) -> int | None:
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar()

    async def get_user_by_email(self, email: str) -> User:
        query = (
            select(User)
            .where(User.email == email)
            .options(load_only(User.id, User.email, User.is_verified))
        )
        result = await self.session.execute(query)
        user = result.scalar()
        return user

    async def update_user_verified_status(self, email: str) -> None:
        stmt = update(User).values(is_verified=True).where(User.email == email)
        await self.session.execute(stmt)
