from typing import List

from fastapi.exceptions import HTTPException
from starlette import status
from starlette.datastructures import UploadFile

from exceptions.base import NotFound, PermissionDenied
from models.posts import Post
from repositories.posts import PostRepository
from utils.upload_image import upload_image


class PostService:
    def __init__(self, post_repo: PostRepository):
        self.post_repo = post_repo

    async def update_data_image_attr(self, data: dict) -> None:
        image = data.get('image')
        if image:
            if isinstance(image, UploadFile):
                uploaded_image_path = await upload_image(image)
                data.update({'image': uploaded_image_path})
            elif isinstance(image, str) and image == ' ':
                data.update({'image': None})
            else:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail='Invalid image type',
                )
        else:
            data.pop('image')

    async def create_post(
            self,
            post: dict,
            user_info: dict,
    ) -> Post:
        await self.update_data_image_attr(post)
        post.setdefault('user_id', user_info.get('user_id'))
        created_post = await self.post_repo.create(post)
        return created_post

    async def get_user_posts(self, user_id: int) -> List[Post]:
        posts = await self.post_repo.get_user_posts(user_id)
        return posts

    async def get_posts(self) -> List[Post]:
        posts = await self.post_repo.get_all()
        return posts

    async def get_post(
            self,
            post_id: int,
    ) -> Post:
        post = await self.post_repo.get_one(post_id)
        if not post:
            raise NotFound
        return post

    async def edit_post(
            self,
            post_id: int,
            update_data: dict,
            user_info: dict,
    ) -> Post:
        instance = await self.post_repo.return_author_id(post_id)
        if not instance:
            raise NotFound
        if user_info.get('user_id') != instance.user_id:
            raise PermissionDenied
        await self.update_data_image_attr(update_data)
        post = await self.post_repo.update(post_id, update_data)
        return post

    async def delete_post(
            self,
            post_id: int,
            user_info: dict,
    ):
        instance = await self.post_repo.return_author_id(post_id)
        if not instance:
            raise NotFound
        if user_info.get('user_id') != instance.user_id:
            raise PermissionDenied
        await self.post_repo.delete(post_id)
