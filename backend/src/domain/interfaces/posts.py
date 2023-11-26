from abc import ABC, abstractmethod


class PostServiceInterface(ABC):
    @staticmethod
    @abstractmethod
    async def update_data_image_attr(
        data: dict,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def create_post(
        self,
        post: dict,
        user_info: dict,
    ):
        raise NotImplementedError

    @abstractmethod
    async def get_user_posts(
        self,
        user_id: int,
    ):
        raise NotImplementedError

    @abstractmethod
    async def get_posts(
        self,
    ):
        raise NotImplementedError

    @abstractmethod
    async def get_post(
        self,
        post_id: int,
    ):
        raise NotImplementedError

    @abstractmethod
    async def edit_post(
        self,
        post_id: int,
        update_data: dict,
        user_info: dict,
    ):
        raise NotImplementedError

    @abstractmethod
    async def delete_post(
        self,
        post_id: int,
        user_info: dict,
    ):
        raise NotImplementedError
