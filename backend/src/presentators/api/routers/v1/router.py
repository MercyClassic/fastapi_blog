from fastapi import APIRouter

from presentators.api.routers.v1 import (
    jwt_router,
    posts_router,
    tags_router,
    users_router,
)

v1_router = APIRouter(prefix='/api/v1')

v1_router.include_router(jwt_router)
v1_router.include_router(posts_router)
v1_router.include_router(tags_router)
v1_router.include_router(users_router)
