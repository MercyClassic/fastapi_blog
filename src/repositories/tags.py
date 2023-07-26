from typing import List

from sqlalchemy import select, insert, delete
from sqlalchemy.orm import load_only

from models.posts import Tag, Post, PostTag
from repositories.base import SQLAlchemyRepository


class TagRepository(SQLAlchemyRepository):
    model = Tag

    async def get_post_tags(self, post_id: int) -> List[Tag]:
        query = (
            select(Tag)
            .options(load_only(Tag.id, Tag.name, Tag.created_at))
            .join(PostTag)
            .join(Post)
            .where(PostTag.post_id == post_id, Post.published == True)
        )
        query = self.paginate_query(query)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def set_post_tag(self, post_tag_data: dict) -> PostTag:
        stmt = (
            insert(PostTag)
            .values(**post_tag_data)
            .returning(PostTag)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def delete_post_tag(self, post_tag_id: int) -> None:
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
