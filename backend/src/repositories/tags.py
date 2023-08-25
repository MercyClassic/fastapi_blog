from typing import List, Type

from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import load_only

from models.posts import Post
from models.tags import PostTag, Tag
from repositories.base import BaseSQLAlchemyRepository
from repositories.posts import PostRepository


class TagRepository(BaseSQLAlchemyRepository):
    async def return_author_id(self, tag_id: int) -> Type[Tag]:
        query = select(Tag).where(Tag.id == tag_id).options(load_only(Tag.user_id))
        instance = await self.session.execute(query)
        return instance.scalar_one()

    async def get_tags(self) -> List[Type[Tag]]:
        query = select(Tag)
        query = self.paginate_query(query)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create_tag(self, data: dict) -> Type[Tag]:
        stmt = insert(Tag).values(**data).returning(Tag)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def update_tag(self, tag_id: int, update_data: dict) -> Type[Tag]:
        stmt = update(Tag).where(Tag.id == tag_id).values(**update_data).returning(Tag)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def delete_tag(self, tag_id: int) -> None:
        stmt = delete(Tag).where(Tag.id == tag_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_post_tags(self, post_id: int) -> List[Type[Tag]]:
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

    async def set_tag_on_post(self, post_tag_data: dict) -> Type[PostTag]:
        stmt = insert(PostTag).values(**post_tag_data).returning(PostTag)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_posts_that_has_specify_tag(self, tag_id: int) -> List[Type[Post]]:
        query = await PostRepository.get_query_with_prefetched_user_and_tags()
        # query = query.where tag.id == tag_id
        result = await self.session.execute(query)
        return result.unique().scalars().all()

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

    async def check_post_author(self, post_tag_id: int) -> Type[Post]:
        query = (
            select(Post)
            .join(PostTag)
            .where(PostTag.id == post_tag_id)
            .options(load_only(Post.user_id))
        )
        result = await self.session.execute(query)
        return result.scalar_one()