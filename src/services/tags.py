from typing import List

from exceptions.base import PermissionDenied, NotFound
from models.posts import PostTag, Tag
from repositories.tags import TagRepository


class TagService:
    def __init__(self, tag_repo: TagRepository):
        self.tag_repo = tag_repo

    async def get_tags(self) -> List[Tag]:
        tags = await self.tag_repo.get_all()
        return tags

    async def create_tag(
            self,
            tag: dict,
            user_info: dict,
    ) -> Tag:
        tag.setdefault('user_id', user_info.get('user_id'))
        tag = await self.tag_repo.create(tag)
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
        await self.tag_repo.delete(tag_id)

    async def edit_tag(
            self,
            tag_id: int,
            update_tag_data: dict,
            user_info: dict,
    ) -> Tag:
        tag = await self.tag_repo.return_author_id(tag_id)
        if not tag:
            raise NotFound
        if user_info.get('user_id') != tag.user_id:
            raise PermissionDenied
        updated_tag = await self.tag_repo.update(tag_id, update_tag_data)
        return updated_tag

    async def get_post_tags(
            self,
            post_id: int,
    ) -> List[Tag]:
        tags = await self.tag_repo.get_post_tags(post_id)
        return tags

    async def set_post_tag(
            self,
            post_id: int,
            post_tag_data: dict,
            user_info: dict,
    ) -> PostTag:
        tag = await self.tag_repo.return_author_id(post_id)
        if not tag:
            raise NotFound
        if user_info.get('user_id') != tag.user_id:
            raise PermissionDenied
        post_tag_data.setdefault('post_id', post_id)
        post_tag = await self.tag_repo.set_post_tag(post_tag_data)
        return post_tag

    async def delete_post_tag(
            self,
            post_tag_id: int,
            user_info: dict,
    ) -> None:
        post = await self.tag_repo.check_post_author(post_tag_id)
        if not post:
            raise NotFound
        if user_info.get('user_id') != post.user_id:
            raise PermissionDenied
        await self.tag_repo.delete_post_tag(post_tag_id)
