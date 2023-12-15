from starlette.datastructures import UploadFile

from app.domain.exceptions.base import NotFound, PermissionDenied
from app.domain.exceptions.users import InvalidImageType
from app.domain.interfaces.posts import PostServiceInterface
from app.domain.utils.upload_image import upload_image
from app.infrastructure.db.uow import UnitOfWorkInterface


class PostService(PostServiceInterface):
    def __init__(
        self,
        uow: UnitOfWorkInterface,
    ):
        self.uow = uow

    @staticmethod
    async def update_data_image_attr(data: dict) -> None:
        image = data.get('image')
        if image:
            if isinstance(image, UploadFile):
                uploaded_image_path = await upload_image(image)
                data.update({'image': uploaded_image_path})
            elif isinstance(image, str) and image == ' ':
                data.update({'image': None})
            else:
                raise InvalidImageType
        else:
            data.pop('image', None)

    async def create_post(
        self,
        post: dict,
        user_info: dict,
    ):
        await self.update_data_image_attr(post)
        post.setdefault('user_id', user_info.get('user_id'))
        created_post = await self.uow.post_repo.create_post(post)
        await self.uow.commit()
        return created_post

    async def get_user_posts(
        self,
        user_id: int,
    ):
        posts = await self.uow.post_repo.get_user_posts(user_id)
        return posts

    async def get_posts(
        self,
    ):
        posts = await self.uow.post_repo.get_posts()
        return posts

    async def get_post(
        self,
        post_id: int,
    ):
        post = await self.uow.post_repo.get_post(post_id)
        if not post:
            raise NotFound
        return post

    async def edit_post(
        self,
        post_id: int,
        update_data: dict,
        user_info: dict,
    ):
        instance = await self.uow.post_repo.return_author_id(post_id)
        if not instance:
            raise NotFound
        if user_info.get('user_id') != instance.user_id:
            raise PermissionDenied
        await self.update_data_image_attr(update_data)
        post = await self.uow.post_repo.update_post(post_id, update_data)
        await self.uow.commit()
        return post

    async def delete_post(
        self,
        post_id: int,
        user_info: dict,
    ):
        instance = await self.uow.post_repo.return_author_id(post_id)
        if not instance:
            raise NotFound
        if user_info.get('user_id') != instance.user_id:
            raise PermissionDenied
        await self.uow.post_repo.delete_post(post_id)
        await self.uow.commit()
