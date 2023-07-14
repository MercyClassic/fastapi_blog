import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.sql.functions import count

from conftest import async_session_maker
from main import app
from src.auth.jwt import generate_jwt
from src.managers.users import UserManager
from src.models.users import User, RefreshToken
from src.config import SECRET_TOKEN_FOR_EMAIL


class TestUser:
    @pytest.mark.parametrize(
        'password1, password2, status_code, result_count',
        [
            ('test', 'test', 201, 1),
            ('tes', 'tes', 422, 1),
            ('te st', 'te st', 422, 1),
            ('%^&*', '%^&*', 422, 1),
        ]
    )
    async def test_register(
            self,
            client: AsyncClient,
            password1: str,
            password2: str,
            status_code: int,
            result_count: int
    ):
        response = await client.post(
            url=app.url_path_for('registration'),
            json={
                'username': 'test',
                'email': 'test@test.ru',
                'password1': password1,
                'password2': password2
            }
        )
        assert response.status_code == status_code

        async with async_session_maker() as session:
            query = select(count(User.id))
            result = await session.execute(query)
            assert result.scalar() == result_count

    async def test_login_without_verify_account(self, client: AsyncClient):
        response = await client.post(
            url=app.url_path_for('login'),
            json={
                'email': 'test@test.ru',
                'input_password': 'test',
            }
        )
        assert response.status_code == 403

    def create_verify_token(self):
        verify_token = generate_jwt(
            data={'id': 1, 'email': 'test@test.ru'},
            lifetime_seconds=60 * 60 * 24 * 3,
            secret=SECRET_TOKEN_FOR_EMAIL
        )
        return verify_token

    async def test_verify_account(self, client: AsyncClient):
        verify_token = self.create_verify_token()
        response = await client.get(app.url_path_for('verify_account', verify_token=verify_token))
        assert response.status_code == 200

    @pytest.mark.parametrize(
        'email, password, status_code',
        [
            ('test@test.ru', 'invalid_password', 422),
            ('test@test.ru', 'test', 200)
        ]
    )
    async def test_login(
            self,
            client: AsyncClient,
            email: str,
            password: str,
            status_code: int
    ):
        response = await client.post(
            url=app.url_path_for('login'),
            json={
                'email': email,
                'input_password': password,
            }
        )
        assert response.status_code == status_code

    async def refresh_access_token(self, client: AsyncClient):
        access_token = client.cookies.get('access_token')
        refresh_token = client.cookies.get('refresh_token')
        response = await client.post(app.url_path_for('refresh_access_token'))
        assert response.status_code == 200
        assert access_token != response.cookies.get('access_token')
        assert refresh_token != response.cookies.get('refresh_token')

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

    async def set_access_token(self, client: AsyncClient):
        async with async_session_maker() as session:
            client.headers['Authorization'] = await UserManager.create_access_token(user_id=1, session=session)

    @pytest.mark.parametrize(
        'with_access_token, status_code',
        [
            (True, 200),
            (False, 401),
        ]
    )
    async def test_get_users(
            self,
            client: AsyncClient,
            with_access_token: bool,
            status_code: int
    ):
        if with_access_token:
            await self.set_access_token(client)
        else:
            client.headers.pop('Authorization')
        response = await client.get(app.url_path_for('get_users'))
        assert response.status_code == status_code

    @pytest.mark.parametrize(
        'with_access_token, status_code',
        [
            (True, 200),
            (False, 401),
        ]
    )
    async def test_fail_get_user(
            self,
            client: AsyncClient,
            with_access_token: bool,
            status_code: int
    ):
        if with_access_token:
            await self.set_access_token(client)
        else:
            client.headers.pop('Authorization')
        response = await client.get(app.url_path_for('get_user', user_id=1))
        assert response.status_code == status_code
