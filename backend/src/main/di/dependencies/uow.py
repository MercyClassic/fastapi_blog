from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.database import get_session_stub
from infrastructure.db.uow import UnitOfWork


async def get_uow(
    session: Annotated[AsyncSession, Depends(get_session_stub)],
) -> UnitOfWork:
    return UnitOfWork(session)
