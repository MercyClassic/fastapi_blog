from starlette.requests import Request

from config import get_settings
from services.jwt import JWTService


def get_jwt_service():
    settings = get_settings()
    return JWTService(
        settings.JWT_ACCESS_SECRET_KEY,
        settings.JWT_REFRESH_SECRET_KEY,
    )


async def get_access_token_from_headers(request: Request) -> str:
    return request.headers.get('Authorization')
