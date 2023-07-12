

def get_pagination_params(limit: int = 10, offset: int = 0) -> dict:
    return {'limit': limit, 'offset': offset}


def get_query_with_pagination_params(query, pagination_params: dict):
    return (
        query
        .limit(pagination_params.get('limit'))
        .offset(pagination_params.get('offset'))
    )
