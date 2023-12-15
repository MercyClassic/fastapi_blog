from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.database import get_session_stub
from app.infrastructure.db.uow import UnitOfWork


async def get_uow(
    session: Annotated[AsyncSession, Depends(get_session_stub)],
) -> UnitOfWork:
    return UnitOfWork(session)
