from typing import Any

from fastapi import HTTPException
from starlette import status


def get_pagination_params(limit: int = 10, offset: int = 0) -> dict:
    return {'limit': limit, 'offset': offset}


def get_stripped_value(value: Any) -> Any:
    value = value.strip()
    if len(value) < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Length value must be atleat 1',
        )
    return value
