import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.sql.functions import count

from conftest import async_session_maker
from main import app
from src.accounts.jwt import generate_jwt
from src.accounts.models import User, RefreshToken
from src.config import SECRET_TOKEN_FOR_EMAIL


class TestUser:
    @pytest.mark.parametrize(
        'password1, password2, status_code, result_count',
        [
            ('test', 'test', 201, 1),
            ('tes', 'tes', 400, 1),
            ('te st', 'te st', 400, 1),
            ('%^&*', '%^&*', 400, 1),
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
        response = await client.post(app.url_path_for('registration'), json={
            'username': 'test',
            'email': 'test@test.ru',
            'password1': password1,
            'password2': password2
        })
        assert response.status_code == status_code

        query = select(count(User.id))
        async with async_session_maker() as session:
            result = await session.execute(query)
            assert result.scalar() == result_count

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

    def save_tokens(self, access_token: str, refresh_token: str):
        self.access_token = access_token
        self.refresh_token = refresh_token

    @pytest.mark.parametrize(
        'email, password, status_code',
        [
            ('test@test.ru', 'test', 200),
            ('test@test.ru', 'invalid_password', 400)
        ]
    )
    async def test_login(
            self,
            client: AsyncClient,
            email: str,
            password: str,
            status_code: int
    ):
        response = await client.post(app.url_path_for('login'), json={
            'email': email,
            'input_password': password,
        })

        """ FOR FUTURE USAGE """
        self.save_tokens(
            access_token=response.cookies.get('access_token'),
            refresh_token=response.cookies.get('refresh_token')
        )

        assert response.status_code == status_code

    async def test_success_get_users(self, client: AsyncClient):
        """ WITH ACCESS TOKEN """
        response = await client.get(app.url_path_for('get_users'))
        assert response.status_code == 200

    @pytest.mark.parametrize(
        'user_id, status_code',
        [
            (1, 200),
            (2, 404)
        ]
    )
    async def test_success_get_user(
            self,
            client: AsyncClient,
            user_id: int,
            status_code: int
    ):
        """ WITH ACCESS TOKEN """
        response = await client.get(app.url_path_for('get_user', user_id=user_id))
        assert response.status_code == status_code

    async def refresh_access_token(self, client: AsyncClient):
        response = await client.post(app.url_path_for('refresh_access_token'))
        assert response.status_code == 200
        assert self.access_token != response.cookies.get('access_token')
        assert self.refresh_token != response.cookies.get('refresh_token')

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

    async def test_fail_get_users(self, client: AsyncClient):
        """ WITHOUT ACCESS TOKEN """
        response = await client.get(app.url_path_for('get_users'))
        assert response.status_code == 403

    async def test_fail_get_user(self, client: AsyncClient):
        """ WITHOUT ACCESS TOKEN """
        response = await client.get(app.url_path_for('get_user', user_id=1))
        assert response.status_code == 403
