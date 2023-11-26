from fastapi import APIRouter

from presentators.api.routers.v1.router import v1_router

root_router = APIRouter()

root_router.include_router(v1_router)
