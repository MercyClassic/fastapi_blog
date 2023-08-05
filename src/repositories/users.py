from typing import List

from sqlalchemy import select, insert, update
from sqlalchemy.orm import load_only

from models.users import User
from repositories.base import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    model = User

    async def get_info_for_authenticate(self, email: str) -> User:
        query = (
            select(self.model)
            .where(self.model.email == email)
            .options(
                load_only(
                    self.model.id, self.model.email, self.model.password,
                    self.model.is_active, self.model.is_verified,
                ),
            )
        )
        result = await self.session.execute(query)
        return result.scalar()

    async def get_all(self, fields: List[str]) -> List[model]:
        query = (
            select(self.model)
            .where(self.model.is_active == True)
            .options(load_only(*fields))
        )
        query = self.paginate_query(query)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_one(
            self,
            user_id: int,
            fields: List[str],
    ) -> model:
        query = (
            select(self.model)
            .where(self.model.id == user_id)
            .options(load_only(*fields))
        )
        result = await self.session.execute(query)
        return result.scalar()

    async def create(
            self,
            user_data: dict,
            hashed_password: str,
    ) -> int:
        stmt = (
            insert(self.model)
            .values(**user_data, password=hashed_password)
            .returning(self.model.id)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def is_user_exists_by_email(self, email: str) -> int | None:
        query = select(self.model).where(self.model.email == email)
        result = await self.session.execute(query)
        return result.scalar()

    async def get_user_by_email(self, email: str) -> model:
        query = (
            select(self.model)
            .where(self.model.email == email)
            .options(load_only(self.model.id, self.model.email, self.model.is_verified))
        )
        result = await self.session.execute(query)
        user = result.scalar()
        return user

    async def update_user_verified_status(self, email: str) -> None:
        stmt = (
            update(self.model)
            .values(is_verified=True)
            .where(self.model.email == email)
        )
        await self.session.execute(stmt)
        await self.session.commit()
