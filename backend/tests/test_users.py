from typing import List

import pytest
from conftest import async_session_maker
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from pydantic import parse_obj_as
from sqlalchemy import select
from sqlalchemy.orm import load_only
from sqlalchemy.sql.functions import count

from application.auth.jwt import generate_jwt
from application.models.users import UserReadBaseSchema
from domain.services.users import UserService
from infrastructure.db.models.jwt import RefreshToken
from infrastructure.db.models.users import User
from main.config import get_settings
from main.main import app

JWT_ACCESS_SECRET_KEY = get_settings().JWT_ACCESS_SECRET_KEY
SECRET_TOKEN_FOR_EMAIL = get_settings().SECRET_TOKEN_FOR_EMAIL


def mock_after_create(*args, **kwargs):
    pass


class TestUser:
    @pytest.mark.parametrize(
        'email, password1, password2, status_code, result_count',
        [
            ('test@test.ru', 'test', 'test', 201, 1),
            ('test2@test.ru', 'tes', 'tes', 422, 1),
            ('test2@test.ru', 'te st', 'te st', 422, 1),
            ('test2@test.ru', '%^&*', '%^&*', 422, 1),
        ],
    )
    async def test_register(
        self,
        client: AsyncClient,
        email: str,
        password1: str,
        password2: str,
        status_code: int,
        result_count: int,
    ):
        UserService.after_create = mock_after_create
        response = await client.post(
            url=app.url_path_for('registration'),
            json={
                'username': 'test',
                'email': email,
                'password1': password1,
                'password2': password2,
            },
        )
        assert response.status_code == status_code

        async with async_session_maker() as session:
            query = select(count(User.id))
            result = await session.execute(query)
            assert result.scalar() == result_count

            query = select(User).where(User.id == 1).options(load_only(User.id, User.is_verified))
            result = await session.execute(query)
            assert result.scalar().is_verified is False

    async def test_login_without_verify_account(self, client: AsyncClient):
        response = await client.post(
            url=app.url_path_for('login'),
            json={
                'email': 'test@test.ru',
                'input_password': 'test',
            },
        )
        assert response.status_code == 403

    @staticmethod
    def create_verify_token():
        verify_token = generate_jwt(
            data={'id': 1, 'email': 'test@test.ru'},
            lifetime_seconds=60 * 60 * 24 * 3,
            secret=SECRET_TOKEN_FOR_EMAIL,
        )
        return verify_token

    async def test_verify_account(self, client: AsyncClient):
        verify_token = self.create_verify_token()
        response = await client.get(app.url_path_for('verify_account', verify_token=verify_token))
        assert response.status_code == 200

        async with async_session_maker() as session:
            query = select(User).where(User.id == 1).options(load_only(User.id, User.is_verified))
            result = await session.execute(query)
            assert result.scalar().is_verified is True

    @pytest.mark.parametrize(
        'email, password, status_code',
        [
            ('test@test.ru', 'invalid_password', 422),
            ('test@test.ru', 'test', 200),
        ],
    )
    async def test_login(
        self,
        client: AsyncClient,
        email: str,
        password: str,
        status_code: int,
    ):
        response = await client.post(
            url=app.url_path_for('login'),
            json={
                'email': email,
                'input_password': password,
            },
        )
        assert response.status_code == status_code

    async def test_refresh_access_token(self, client: AsyncClient):
        response = await client.post(app.url_path_for('refresh_access_token'))
        assert response.status_code == 200

        query = select(count(RefreshToken.id))
        async with async_session_maker() as session:
            result = await session.execute(query)
            assert result.scalar() == 1

    async def test_logout(self, client: AsyncClient):
        response = await client.post(app.url_path_for('logout'))
        assert response.status_code == 401
        assert response.cookies.get('access_token') is None
        assert response.cookies.get('refresh_token') is None

        query = select(count(RefreshToken.id))
        async with async_session_maker() as session:
            result = await session.execute(query)
            assert result.scalar() == 0

    @staticmethod
    async def set_access_token(client: AsyncClient):
        client.headers['Authorization'] = generate_jwt(
            data={'sub': 1},
            secret=JWT_ACCESS_SECRET_KEY,
            lifetime_seconds=60,
        )

    @pytest.mark.parametrize(
        'with_access_token, status_code',
        [
            (True, 200),
            (False, 401),
        ],
    )
    async def test_get_users(
        self,
        client: AsyncClient,
        with_access_token: bool,
        status_code: int,
    ):
        if with_access_token:
            await self.set_access_token(client)
        else:
            client.headers.pop('Authorization')
        response = await client.get(app.url_path_for('get_users'))
        assert response.status_code == status_code

        if with_access_token:
            async with async_session_maker() as session:
                query = select(User)
                result = await session.execute(query)
                assert response.json() == jsonable_encoder(
                    parse_obj_as(
                        List[UserReadBaseSchema],
                        result.scalars().all(),
                    ),
                )

    @pytest.mark.parametrize(
        'with_access_token, status_code',
        [
            (True, 200),
            (False, 401),
        ],
    )
    async def test_fail_get_user(
        self,
        client: AsyncClient,
        with_access_token: bool,
        status_code: int,
    ):
        if with_access_token:
            await self.set_access_token(client)
        else:
            client.headers.pop('Authorization')
        response = await client.get(app.url_path_for('get_user', user_id=1))
        assert response.status_code == status_code
