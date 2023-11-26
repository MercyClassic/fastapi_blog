from typing import List

from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import load_only

from infrastructure.db.interfaces.tags import TagRepositoryInterface
from infrastructure.db.models.posts import Post
from infrastructure.db.models.tags import PostTag, Tag


class TagRepository(TagRepositoryInterface):
    async def return_author_id(self, tag_id: int) -> Tag:
        query = select(Tag).where(Tag.id == tag_id).options(load_only(Tag.user_id))
        instance = await self.session.execute(query)
        return instance.scalar_one()

    async def get_tags(self) -> List[Tag]:
        query = select(Tag)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create_tag(self, data: dict) -> Tag:
        stmt = insert(Tag).values(**data).returning(Tag)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def update_tag(self, tag_id: int, update_data: dict) -> Tag:
        stmt = update(Tag).where(Tag.id == tag_id).values(**update_data).returning(Tag)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def delete_tag(self, tag_id: int) -> None:
        stmt = delete(Tag).where(Tag.id == tag_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_post_tags(self, post_id: int) -> List[Tag]:
        query = (
            select(Tag)
            .options(load_only(Tag.id, Tag.name, Tag.created_at))
            .join(PostTag)
            .join(Post)
            .where(PostTag.post_id == post_id, Post.published.is_(True))
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def set_tag_on_post(self, post_tag_data: dict) -> PostTag:
        stmt = insert(PostTag).values(**post_tag_data).returning(PostTag)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_post_tag_id(self, tag_id: int, post_id: int) -> int:
        query = (
            select(PostTag)
            .join(Tag)
            .join(Post)
            .options(load_only(PostTag.id))
            .where(Tag.id == tag_id, Post.id == post_id)
        )
        result = await self.session.execute(query)
        return result.scalar().id

    async def delete_tag_on_post(self, post_tag_id: int) -> None:
        stmt = delete(PostTag).where(PostTag.id == post_tag_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def check_post_author(self, post_tag_id: int) -> Post:
        query = (
            select(Post)
            .join(PostTag)
            .where(PostTag.id == post_tag_id)
            .options(load_only(Post.user_id))
        )
        result = await self.session.execute(query)
        return result.scalar_one()
