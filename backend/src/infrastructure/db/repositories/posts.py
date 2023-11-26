from typing import List

from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import joinedload, load_only

from infrastructure.db.interfaces.posts import PostRepositoryInterface
from infrastructure.db.models.posts import Post
from infrastructure.db.models.tags import Tag
from infrastructure.db.models.users import User


class PostRepository(PostRepositoryInterface):
    async def return_author_id(self, post_id: int):
        query = select(Post).where(Post.id == post_id).options(load_only(Post.user_id))
        instance = await self.session.execute(query)
        return instance.scalar_one()

    async def get_user_posts(self, user_id: int) -> List[Post]:
        query = await self.get_query_with_prefetched_user_and_tags()
        query = query.where(Post.user_id == user_id)
        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def get_posts(self) -> List[Post]:
        query = await self.get_query_with_prefetched_user_and_tags()
        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def get_post(self, post_id: int) -> Post:
        query = await self.get_query_with_prefetched_user_and_tags()
        query = query.where(
            Post.id == post_id,
            Post.published.is_(True),
        )
        result = await self.session.execute(query)
        return result.unique().scalar_one()

    async def create_post(self, data: dict) -> Post:
        stmt = insert(Post).values(**data).returning(Post)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def update_post(self, post_id: int, update_data: dict) -> Post:
        stmt = update(Post).where(Post.id == post_id).values(**update_data).returning(Post)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def delete_post(self, post_id: int) -> None:
        stmt = delete(Post).where(Post.id == post_id)
        await self.session.execute(stmt)

    @staticmethod
    async def get_query_with_prefetched_user_and_tags():
        return (
            select(Post)
            .where(Post.published.is_(True))
            .options(
                load_only(
                    Post.id,
                    Post.title,
                    Post.content,
                    Post.created_at,
                    Post.published,
                    Post.image,
                ),
            )
            .options(
                joinedload(Post.user).options(load_only(User.id, User.username)),
                joinedload(Post.tags).options(load_only(Tag.id, Tag.name, Tag.created_at)),
            )
        )
