from typing import List

import pytest
from conftest import async_session_maker
from fastapi import UploadFile
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from pydantic import parse_obj_as
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from auth.jwt import generate_jwt
from config import get_settings
from main import app
from managers.users import UserManager
from models.posts import Post
from models.users import User
from repositories.posts import PostRepository
from schemas.posts import PostReadSchema

JWT_ACCESS_SECRET_KEY = get_settings().JWT_ACCESS_SECRET_KEY


class TestPost:
    @pytest.fixture(scope='module', autouse=True)
    async def setup(self, client: AsyncClient):
        async with async_session_maker() as session:
            users_data = [
                {'username': 'test', 'email': 'test@test.ru'},
                {'username': 'test', 'email': 'test2@test.ru'},
            ]
            for user in users_data:
                stmt = insert(User).values(
                    username=user['username'],
                    email=user['email'],
                    password=UserManager.make_password('test'),
                )
                await session.execute(stmt)

            await session.commit()
            client.headers['Authorization'] = generate_jwt(
                data={'sub': 1},
                secret=JWT_ACCESS_SECRET_KEY,
                lifetime_seconds=60,
            )

    @staticmethod
    async def set_current_access_token(client: AsyncClient, by_author: bool):
        """USER WITH ID = 1 IS AUTHOR"""
        if by_author:
            client.headers['Authorization'] = generate_jwt(
                data={'sub': 1},
                secret=JWT_ACCESS_SECRET_KEY,
                lifetime_seconds=60,
            )
        else:
            client.headers['Authorization'] = generate_jwt(
                data={'sub': 2},
                secret=JWT_ACCESS_SECRET_KEY,
                lifetime_seconds=60,
            )

    @staticmethod
    async def assert_count(model, result_count: int):
        async with async_session_maker() as session:
            query = select(count(model.id))
            result = await session.execute(query)
            assert result.scalar() == result_count

    @pytest.mark.parametrize(
        'title, content, published, image, status_code, result_count',
        [
            ('test', 'test', True, None, 201, 1),
            ('test', 'test', False, None, 201, 2),
            ('test' * 13, 'test', True, None, 422, 2),
            ('test', 'test' * 251, True, None, 422, 2),
            ('    ', '1', True, None, 422, 2),
            ('1', '    ', True, None, 422, 2),
        ],
    )
    async def test_create_post(
        self,
        client: AsyncClient,
        title: str,
        content: str,
        published: bool,
        image: UploadFile | None | str,
        status_code: int,
        result_count: int,
    ):
        response = await client.post(
            url=app.url_path_for('create_post'),
            data={
                'title': title,
                'content': content,
                'published': published,
                'image': image,
            },
        )
        assert response.status_code == status_code

        await self.assert_count(Post, result_count)

    @pytest.mark.parametrize(
        'post_id, title, content, published, image, by_author, should_match, status_code',
        [
            (1, 'edited', 'edited', True, None, True, True, 200),
            (2, 'edited', 'edited', False, None, True, True, 200),
            (1, 'test' * 13, 'test', False, None, True, False, 422),
            (1, 'test', 'test' * 251, False, None, True, False, 422),
            (1, '    ', '1', False, None, True, False, 422),
            (1, '1', '    ', False, None, True, False, 422),
            (1, 'edited2', 'edited2', False, None, False, False, 403),
        ],
    )
    async def test_edit_post(
        self,
        client: AsyncClient,
        session: AsyncSession,
        post_id: int,
        title: str,
        content: str,
        published: bool,
        image: UploadFile | None | str,
        by_author: bool,
        should_match: bool,
        status_code: int,
    ):
        await self.set_current_access_token(client, by_author)
        response = await client.patch(
            url=app.url_path_for('edit_post', post_id=post_id),
            data={
                'title': title,
                'content': content,
                'published': published,
                'image': image,
            },
        )
        assert response.status_code == status_code

        query = select(Post).where(Post.id == post_id)
        result = await session.execute(query)
        post = result.scalar()
        if should_match:
            assert post.title == title
            assert post.content == content
            assert post.published == published
        else:
            assert post.title != title
            assert post.content != content
            assert post.published != published

    @pytest.mark.parametrize(
        'post_id, by_author, status_code, result_count',
        [
            (2, False, 403, 2),
            (2, True, 204, 1),
        ],
    )
    async def test_delete_post(
        self,
        client: AsyncClient,
        post_id: int,
        by_author: bool,
        status_code: int,
        result_count: int,
    ):
        await self.set_current_access_token(client, by_author)
        response = await client.delete(app.url_path_for('delete_post', post_id=post_id))
        assert response.status_code == status_code

        await self.assert_count(Post, result_count)

    async def test_get_posts(self, client: AsyncClient, session: AsyncSession):
        response = await client.get(app.url_path_for('get_posts'))
        assert response.status_code == 200

        query = await PostRepository.get_query_with_prefetched_user_and_tags()
        result = await session.execute(query)
        assert response.json() == jsonable_encoder(
            parse_obj_as(
                List[PostReadSchema],
                result.unique().scalars().all(),
            ),
        )

    async def test_get_post(self, client: AsyncClient, session: AsyncSession):
        response = await client.get(app.url_path_for('get_post', post_id=1))
        assert response.status_code == 200

        query = await PostRepository.get_query_with_prefetched_user_and_tags()
        result = await session.execute(query)
        assert response.json() == jsonable_encoder(
            parse_obj_as(
                PostReadSchema,
                result.unique().scalar(),
            ),
        )
