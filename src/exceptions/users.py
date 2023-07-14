from fastapi.exceptions import HTTPException
from starlette import status


class InvalidToken(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Invalid token'
        )
