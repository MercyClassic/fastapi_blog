from abc import ABC, abstractmethod

from exceptions.base import NotFound, PermissionDenied
from uow import UnitOfWorkInterface


class TagServiceInterface(ABC):
    @abstractmethod
    async def get_tags(
        self,
        uow: UnitOfWorkInterface,
    ):
        raise NotImplementedError

    @abstractmethod
    async def create_tag(
        self,
        tag: dict,
        user_info: dict,
        uow: UnitOfWorkInterface,
    ):
        raise NotImplementedError

    @abstractmethod
    async def delete_tag(
        self,
        tag_id: int,
        user_info: dict,
        uow: UnitOfWorkInterface,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def edit_tag(
        self,
        tag_id: int,
        update_tag_data: dict,
        user_info: dict,
        uow: UnitOfWorkInterface,
    ):
        raise NotImplementedError

    @abstractmethod
    async def set_tag_on_post(
        self,
        post_id: int,
        post_tag_data: dict,
        user_info: dict,
        uow: UnitOfWorkInterface,
    ):
        raise NotImplementedError

    @abstractmethod
    async def delete_tag_on_post(
        self,
        tag_id: int,
        post_id: int,
        user_info: dict,
        uow: UnitOfWorkInterface,
    ) -> None:
        raise NotImplementedError


class TagService(TagServiceInterface):
    async def get_tags(
        self,
        uow: UnitOfWorkInterface,
    ):
        async with uow:
            tags = await uow.tag_repo.get_tags()
        return tags

    async def create_tag(
        self,
        tag: dict,
        user_info: dict,
        uow: UnitOfWorkInterface,
    ):
        tag.setdefault('user_id', user_info.get('user_id'))
        async with uow:
            tag = await uow.tag_repo.create_tag(tag)
        return tag

    async def delete_tag(
        self,
        tag_id: int,
        user_info: dict,
        uow: UnitOfWorkInterface,
    ) -> None:
        async with uow:
            tag = await uow.tag_repo.return_author_id(tag_id)
            if not tag:
                raise NotFound
            if user_info.get('user_id') != tag.user_id:
                raise PermissionDenied
            await uow.tag_repo.delete_tag(tag_id)
            await uow.commit()

    async def edit_tag(
        self,
        tag_id: int,
        update_tag_data: dict,
        user_info: dict,
        uow: UnitOfWorkInterface,
    ):
        async with uow:
            tag = await uow.tag_repo.return_author_id(tag_id)
            if not tag:
                raise NotFound
            if user_info.get('user_id') != tag.user_id:
                raise PermissionDenied
            updated_tag = await uow.tag_repo.update_tag(tag_id, update_tag_data)
            await uow.commit()
        return updated_tag

    async def set_tag_on_post(
        self,
        post_id: int,
        post_tag_data: dict,
        user_info: dict,
        uow: UnitOfWorkInterface,
    ):
        async with uow:
            tag = await uow.tag_repo.return_author_id(post_id)
            if not tag:
                raise NotFound
            if user_info.get('user_id') != tag.user_id:
                raise PermissionDenied
            post_tag_data.setdefault('post_id', post_id)
            post_tag = await uow.tag_repo.set_tag_on_post(post_tag_data)
            await uow.commit()
        return post_tag

    async def delete_tag_on_post(
        self,
        tag_id: int,
        post_id: int,
        user_info: dict,
        uow: UnitOfWorkInterface,
    ) -> None:
        async with uow:
            post = await uow.tag_repo.check_post_author(post_id)
            if not post:
                raise NotFound
            if user_info.get('user_id') != post.user_id:
                raise PermissionDenied
            post_tag_id = await uow.tag_repo.get_post_tag_id(tag_id, post_id)
            await uow.tag_repo.delete_tag_on_post(post_tag_id)
