import pytest
from fastapi import UploadFile
from httpx import AsyncClient
from sqlalchemy import insert, select
from sqlalchemy.sql.functions import count

from src.models.posts import Post
from tests.conftest import async_session_maker
from src.managers.users import UserManager
from src.models.users import User
from main import app


class TestPost:
    @pytest.fixture(scope='module', autouse=True)
    async def setup(self, client: AsyncClient):
        async with async_session_maker() as session:
            users_data = [
                {'username': 'test', 'email': 'test@test.ru'},
                {'username': 'test', 'email': 'test2@test.ru'}
            ]
            for user in users_data:
                stmt = insert(User).values(
                    username=user['username'],
                    email=user['email'],
                    password=UserManager.make_password('test'),
                )
                await session.execute(stmt)

            await session.commit()
            client.headers['Authorization'] = await UserManager.create_access_token(user_id=1, session=session)

    async def set_current_access_token(self, client: AsyncClient, by_author: bool):
        """ USER WITH ID = 1 IS AUTHOR """
        async with async_session_maker() as session:
            if by_author:
                client.headers['Authorization'] = await UserManager.create_access_token(user_id=1, session=session)
            else:
                client.headers['Authorization'] = await UserManager.create_access_token(user_id=2, session=session)

    async def assert_count(self, model, result_count: int):
        async with async_session_maker() as session:
            query = select(count(model.id))
            result = await session.execute(query)
            assert result.scalar() == result_count

    @pytest.mark.parametrize(
        'title, content, published, image, status_code, result_count',
        [
            ('test', 'test', True, None, 201, 1),
            ('test', 'test', False, None, 201, 2),
            ('test'*13, 'test', True, None, 422, 2),
            ('test', 'test'*251, True, None, 422, 2),
            ('    ', '1', True, None, 422, 2),
            ('1', '    ', True, None, 422, 2)
        ]
    )
    async def test_create_post(
            self,
            client: AsyncClient,
            title: str,
            content: str,
            published: bool,
            image: UploadFile | None | str,
            status_code: int,
            result_count: int
    ):
        response = await client.post(
            url=app.url_path_for('create_post'),
            data={
                'title': title,
                'content': content,
                'published': published,
                'image': image
            }
        )
        assert response.status_code == status_code

        await self.assert_count(Post, result_count)

    @pytest.mark.parametrize(
        'post_id, title, content, published, image, by_author, status_code',
        [
            (1, 'edited', 'edited', True, None, True, 200),
            (2, 'edited', 'edited', False, None, True, 200),
            (1, 'test'*13, 'test', True, None, True, 422),
            (1, 'test', 'test'*251, True, None, True, 422),
            (1, '    ', '1', True, None, True, 422),
            (1, '1', '    ', True, None, True, 422),
            (1, 'edited', 'edited', True, None, False, 403)
        ]
    )
    async def test_edit_post(
            self,
            client: AsyncClient,
            post_id: int,
            title: str,
            content: str,
            published: bool,
            image: UploadFile | None | str,
            by_author: bool,
            status_code: int
    ):
        await self.set_current_access_token(client, by_author)
        response = await client.put(
            url=app.url_path_for('edit_post', post_id=post_id),
            data={
                'title': title,
                'content': content,
                'published': published,
                'image': image
            }
        )
        assert response.status_code == status_code

    @pytest.mark.parametrize(
        'post_id, by_author, status_code, result_count',
        [
            (2, False, 403, 2),
            (2, True, 204, 1),
        ]
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

    async def test_get_posts(self, client: AsyncClient):
        response = await client.get(app.url_path_for('get_posts'))
        assert response.status_code == 200

    async def test_get_post(self, client: AsyncClient):
        response = await client.get(app.url_path_for('get_post', post_id=1))
        assert response.status_code == 200
