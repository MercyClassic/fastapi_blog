from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.accounts.manager import UserManager
from src.accounts.models import User


async def get_current_user(access_token: str, session: AsyncSession) -> User:
    user_id = UserManager.get_user_id_from_access_token(access_token)
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    await session.commit()
    user = result.scalar()
    return user
