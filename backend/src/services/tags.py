from typing import List, Type

from exceptions.base import NotFound, PermissionDenied
from models.posts import Post
from models.tags import PostTag, Tag
from repositories.tags import TagRepository


class TagService:
    def __init__(self, tag_repo: TagRepository):
        self.tag_repo = tag_repo

    async def get_tags(self) -> List[Type[Tag]]:
        tags = await self.tag_repo.get_tags()
        return tags

    async def create_tag(
        self,
        tag: dict,
        user_info: dict,
    ) -> Type[Tag]:
        tag.setdefault('user_id', user_info.get('user_id'))
        tag = await self.tag_repo.create_tag(tag)
        return tag

    async def delete_tag(
        self,
        tag_id: int,
        user_info: dict,
    ) -> None:
        tag = await self.tag_repo.return_author_id(tag_id)
        if not tag:
            raise NotFound
        if user_info.get('user_id') != tag.user_id:
            raise PermissionDenied
        await self.tag_repo.delete_tag(tag_id)

    async def edit_tag(
        self,
        tag_id: int,
        update_tag_data: dict,
        user_info: dict,
    ) -> Type[Tag]:
        tag = await self.tag_repo.return_author_id(tag_id)
        if not tag:
            raise NotFound
        if user_info.get('user_id') != tag.user_id:
            raise PermissionDenied
        updated_tag = await self.tag_repo.update_tag(tag_id, update_tag_data)
        return updated_tag

    async def set_tag_on_post(
        self,
        post_id: int,
        post_tag_data: dict,
        user_info: dict,
    ) -> Type[PostTag]:
        tag = await self.tag_repo.return_author_id(post_id)
        if not tag:
            raise NotFound
        if user_info.get('user_id') != tag.user_id:
            raise PermissionDenied
        post_tag_data.setdefault('post_id', post_id)
        post_tag = await self.tag_repo.set_tag_on_post(post_tag_data)
        return post_tag

    async def get_posts_that_has_specify_tag(
        self,
        tag_id: int,
    ) -> List[Type[Post]]:
        posts = await self.tag_repo.get_posts_that_has_specify_tag(tag_id)
        return posts

    async def delete_tag_on_post(
        self,
        tag_id: int,
        post_id: int,
        user_info: dict,
    ) -> None:
        post = await self.tag_repo.check_post_author(post_id)
        if not post:
            raise NotFound
        if user_info.get('user_id') != post.user_id:
            raise PermissionDenied
        post_tag_id = await self.tag_repo.get_post_tag_id(tag_id, post_id)
        await self.tag_repo.delete_tag_on_post(post_tag_id)
