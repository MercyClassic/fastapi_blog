from typing import List

import pytest
from conftest import async_session_maker
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from pydantic import parse_obj_as
from sqlalchemy import select
from sqlalchemy.orm import load_only
from sqlalchemy.sql.functions import count

from auth.auth import create_access_token
from auth.jwt import generate_jwt
from config import SECRET_TOKEN_FOR_EMAIL
from main import app
from models.users import RefreshToken, User
from schemas.users import UserReadBaseSchema


class TestUser:
    @pytest.mark.parametrize(
        'password1, password2, status_code, result_count',
        [
            ('test', 'test', 201, 1),
            ('tes', 'tes', 422, 1),
            ('te st', 'te st', 422, 1),
            ('%^&*', '%^&*', 422, 1),
        ],
    )
    async def test_register(
            self,
            client: AsyncClient,
            password1: str,
            password2: str,
            status_code: int,
            result_count: int,
    ):
        response = await client.post(
            url=app.url_path_for('registration'),
            json={
                'username': 'test',
                'email': 'test@test.ru',
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
        async with async_session_maker() as session:
            client.headers['Authorization'] = await create_access_token(
                user_id=1, session=session,
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
                        List[UserReadBaseSchema], result.scalars().all(),
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
