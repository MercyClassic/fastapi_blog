from sqlalchemy.ext.asyncio import AsyncSession


class SQLAlchemyBaseGateway:
    def __init__(self, session: AsyncSession):
        self.session = session
