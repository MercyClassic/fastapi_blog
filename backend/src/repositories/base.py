from sqlalchemy.ext.asyncio import AsyncSession


class BaseSQLAlchemyRepository:
    def __init__(
        self,
        session: AsyncSession,
        pagination_params: dict = None,
    ):
        if not pagination_params:
            pagination_params = {'limit': 10, 'offset': 0}
        self.session = session
        self.limit = pagination_params.get('limit')
        self.offset = pagination_params.get('offset')

    def paginate_query(self, query):
        return query.offset(self.offset).limit(self.limit)
