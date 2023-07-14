import pytest
from httpx import AsyncClient
from sqlalchemy.sql.functions import count

from src.managers.users import UserManager
from src.models.posts import Post, Tag, PostTag
from src.models.users import User
from tests.conftest import async_session_maker
from sqlalchemy import insert, select
from main import app


class TestTag:
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

            stmt = insert(Post).values(
                user_id=1,
                title='test',
                content='test',
                published=True,
            )
            await session.execute(stmt)

            await session.commit()

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
        'name, with_authorization, status_code, result_count',
        [
            ('test', False, 401, 0),
            ('test', True, 201, 1),
            ('test', True, 201, 2),
            (' ', True, 422, 2)
        ]
    )
    async def test_create_tag(
            self,
            client: AsyncClient,
            name: str,
            with_authorization: bool,
            status_code: int,
            result_count: int
    ):
        if with_authorization:
            async with async_session_maker() as session:
                client.headers['Authorization'] = await UserManager.create_access_token(user_id=1, session=session)
        else:
            client.headers.pop('Authorization', None)
        response = await client.post(
            url=app.url_path_for('create_tag'),
            json={
                'name': name
            }
        )
        assert response.status_code == status_code

        await self.assert_count(Tag, result_count)

    async def test_get_tags(self, client: AsyncClient):
        response = await client.get(app.url_path_for('get_tags'))
        assert response.status_code == 200

    @pytest.mark.parametrize(
        'name, by_author, status_code',
        [
            ('edited', True, 200),
            ('   ', True, 422),
            ('edit not by author', False, 403),
        ]
    )
    async def test_edit_tag(
            self,
            client: AsyncClient,
            name: str,
            by_author: bool,
            status_code: int
    ):
        await self.set_current_access_token(client, by_author)
        response = await client.patch(
            url=app.url_path_for('edit_tag', tag_id=1),
            json={
                'name': name
            }
        )
        assert response.status_code == status_code

    @pytest.mark.parametrize(
        'tag_id, by_author, status_code, result_count',
        [
            (1, False, 403, 0),
            (1, True, 201, 1),
            (2, True, 201, 2)
        ]
    )
    async def test_set_post_tag(
            self,
            client: AsyncClient,
            tag_id: int,
            by_author: bool,
            status_code: int,
            result_count: int
    ):
        await self.set_current_access_token(client, by_author)
        response = await client.post(
            url=app.url_path_for('set_post_tag', post_id=1),
            json={
                'tag_id': 1
            }
        )
        assert response.status_code == status_code

        await self.assert_count(PostTag, result_count)

    async def test_get_post_tags(self, client: AsyncClient):
        response = await client.get(app.url_path_for('get_post_tags', post_id=1))
        assert response.status_code == 200
        assert len(response.json()) == 2

    @pytest.mark.parametrize(
        'posttag_id, by_author, status_code, result_count',
        [
            (1, False, 403, 2),
            (1, True, 204, 1),
            (2, True, 204, 0)
        ]
    )
    async def test_delete_post_tag(
            self,
            client: AsyncClient,
            posttag_id: int,
            by_author: bool,
            status_code: int,
            result_count: int
    ):
        await self.set_current_access_token(client, by_author)
        response = await client.delete(app.url_path_for('delete_post_tag', posttag_id=posttag_id))
        assert response.status_code == status_code

        await self.assert_count(PostTag, result_count)
