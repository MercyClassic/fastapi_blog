from app.domain.exceptions.base import NotFound, PermissionDenied
from app.domain.interfaces.tags import TagServiceInterface
from app.infrastructure.db.uow import UnitOfWorkInterface


class TagService(TagServiceInterface):
    def __init__(
        self,
        uow: UnitOfWorkInterface,
    ):
        self.uow = uow

    async def get_tags(
        self,
    ):
        tags = await self.uow.tag_repo.get_tags()
        return tags

    async def create_tag(
        self,
        tag: dict,
        user_info: dict,
    ):
        tag.setdefault('user_id', user_info.get('user_id'))
        tag = await self.uow.tag_repo.create_tag(tag)
        return tag

    async def delete_tag(
        self,
        tag_id: int,
        user_info: dict,
    ) -> None:
        tag = await self.uow.tag_repo.return_author_id(tag_id)
        if not tag:
            raise NotFound
        if user_info.get('user_id') != tag.user_id:
            raise PermissionDenied
        await self.uow.tag_repo.delete_tag(tag_id)
        await self.uow.commit()

    async def edit_tag(
        self,
        tag_id: int,
        update_tag_data: dict,
        user_info: dict,
    ):
        tag = await self.uow.tag_repo.return_author_id(tag_id)
        if not tag:
            raise NotFound
        if user_info.get('user_id') != tag.user_id:
            raise PermissionDenied
        updated_tag = await self.uow.tag_repo.update_tag(tag_id, update_tag_data)
        await self.uow.commit()
        return updated_tag

    async def set_tag_on_post(
        self,
        post_id: int,
        post_tag_data: dict,
        user_info: dict,
    ):
        tag = await self.uow.tag_repo.return_author_id(post_id)
        if not tag:
            raise NotFound
        if user_info.get('user_id') != tag.user_id:
            raise PermissionDenied
        post_tag_data.setdefault('post_id', post_id)
        post_tag = await self.uow.tag_repo.set_tag_on_post(post_tag_data)
        await self.uow.commit()
        return post_tag

    async def delete_tag_on_post(
        self,
        tag_id: int,
        post_id: int,
        user_info: dict,
    ) -> None:
        post = await self.uow.tag_repo.check_post_author(post_id)
        if not post:
            raise NotFound
        if user_info.get('user_id') != post.user_id:
            raise PermissionDenied
        post_tag_id = await self.uow.tag_repo.get_post_tag_id(tag_id, post_id)
        await self.uow.tag_repo.delete_tag_on_post(post_tag_id)
