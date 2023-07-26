from typing import List

from models.posts import Post
from repositories.base import SQLAlchemyRepository
from utils.posts import query_with_prefetched_user_and_tags


class PostRepository(SQLAlchemyRepository):
    model = Post

    async def get_user_posts(self, user_id: int) -> List[Post]:
        query = query_with_prefetched_user_and_tags.where(Post.user_id == user_id)
        query = self.paginate_query(query)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_all(self) -> List[Post]:
        query = query_with_prefetched_user_and_tags.where(Post.published == True)
        query = self.paginate_query(query)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_one(self, post_id: int) -> Post:
        query = query_with_prefetched_user_and_tags.where(
            Post.id == post_id, Post.published == True,
        )
        result = await self.session.execute(query)
        return result.scalar_one()
