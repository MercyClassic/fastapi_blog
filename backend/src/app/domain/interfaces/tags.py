from abc import ABC, abstractmethod


class TagServiceInterface(ABC):
    @abstractmethod
    async def get_tags(
        self,
    ):
        raise NotImplementedError

    @abstractmethod
    async def create_tag(
        self,
        tag: dict,
        user_info: dict,
    ):
        raise NotImplementedError

    @abstractmethod
    async def delete_tag(
        self,
        tag_id: int,
        user_info: dict,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def edit_tag(
        self,
        tag_id: int,
        update_tag_data: dict,
        user_info: dict,
    ):
        raise NotImplementedError

    @abstractmethod
    async def set_tag_on_post(
        self,
        post_id: int,
        post_tag_data: dict,
        user_info: dict,
    ):
        raise NotImplementedError

    @abstractmethod
    async def delete_tag_on_post(
        self,
        tag_id: int,
        post_id: int,
        user_info: dict,
    ) -> None:
        raise NotImplementedError
