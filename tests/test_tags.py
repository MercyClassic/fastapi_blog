from typing import List

import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from pydantic import parse_obj_as
from sqlalchemy import insert, select
from sqlalchemy.orm import load_only
from sqlalchemy.sql.functions import count

from auth.auth import create_access_token
from main import app
from managers.users import UserManager
from models.posts import Post, PostTag, Tag
from models.users import User
from schemas.posts import TagReadSchema
from tests.conftest import async_session_maker


class TestTag:
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

            stmt = insert(Post).values(
                user_id=1,
                title='test',
                content='test',
                published=True,
            )
            await session.execute(stmt)

            await session.commit()

    @staticmethod
    async def set_current_access_token(client: AsyncClient, by_author: bool):
        """ USER WITH ID = 1 IS AUTHOR """
        async with async_session_maker() as session:
            if by_author:
                client.headers['Authorization'] = await create_access_token(
                    user_id=1, session=session,
                )
            else:
                client.headers['Authorization'] = await create_access_token(
                    user_id=2, session=session,
                )

    @staticmethod
    async def assert_count(model, result_count: int):
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
            (' ', True, 422, 2),
        ],
    )
    async def test_create_tag(
            self,
            client: AsyncClient,
            name: str,
            with_authorization: bool,
            status_code: int,
            result_count: int,
    ):
        if with_authorization:
            async with async_session_maker() as session:
                client.headers['Authorization'] = await create_access_token(
                    user_id=1, session=session,
                )
        else:
            client.headers.pop('Authorization', None)
        response = await client.post(
            url=app.url_path_for('create_tag'),
            json={
                'name': name,
            },
        )
        assert response.status_code == status_code

        await self.assert_count(Tag, result_count)

    async def test_get_tags(self, client: AsyncClient):
        response = await client.get(app.url_path_for('get_tags'))
        assert response.status_code == 200

        async with async_session_maker() as session:
            query = select(Tag)
            result = await session.execute(query)
            assert response.json() == jsonable_encoder(
                parse_obj_as(
                    List[TagReadSchema], result.scalars().all(),
                ),
            )

    @pytest.mark.parametrize(
        'name, by_author, should_match, status_code',
        [
            ('edited', True, True, 200),
            ('   ', False, False, 422),
            ('edit not by author', False, False, 403),
        ],
    )
    async def test_edit_tag(
            self,
            client: AsyncClient,
            name: str,
            by_author: bool,
            should_match: bool,
            status_code: int,
    ):
        await self.set_current_access_token(client, by_author)
        response = await client.patch(
            url=app.url_path_for('edit_tag', tag_id=1),
            json={
                'name': name,
            },
        )
        assert response.status_code == status_code

        async with async_session_maker() as session:
            query = select(Tag).where(Tag.id == 1)
            result = await session.execute(query)
            tag = parse_obj_as(TagReadSchema, result.scalar())
            if should_match:
                assert tag.name == name
            else:
                assert tag.name != name

    @pytest.mark.parametrize(
        'tag_id, by_author, status_code, result_count',
        [
            (1, False, 403, 0),
            (1, True, 201, 1),
            (2, True, 201, 2),
        ],
    )
    async def test_set_post_tag(
            self,
            client: AsyncClient,
            tag_id: int,
            by_author: bool,
            status_code: int,
            result_count: int,
    ):
        await self.set_current_access_token(client, by_author)
        response = await client.post(
            url=app.url_path_for('set_post_tag', post_id=1),
            json={
                'tag_id': 1,
            },
        )
        assert response.status_code == status_code

        await self.assert_count(PostTag, result_count)

    async def test_get_post_tags(self, client: AsyncClient):
        response = await client.get(app.url_path_for('get_post_tags', post_id=1))
        assert response.status_code == 200

        async with async_session_maker() as session:
            query = (
                select(Tag)
                .options(load_only(Tag.id, Tag.name, Tag.created_at))
                .join(PostTag)
                .join(Post)
                .where(PostTag.post_id == 1, Post.published is True)
            )
            result = await session.execute(query)
        assert response.json() == jsonable_encoder(
            parse_obj_as(
                List[TagReadSchema], result.scalars().all(),
            ),
        )

    @pytest.mark.parametrize(
        'posttag_id, by_author, status_code, result_count',
        [
            (1, False, 403, 2),
            (1, True, 204, 1),
            (2, True, 204, 0),
        ],
    )
    async def test_delete_post_tag(
            self,
            client: AsyncClient,
            posttag_id: int,
            by_author: bool,
            status_code: int,
            result_count: int,
    ):
        await self.set_current_access_token(client, by_author)
        response = await client.delete(app.url_path_for('delete_post_tag', posttag_id=posttag_id))
        assert response.status_code == status_code

        await self.assert_count(PostTag, result_count)
