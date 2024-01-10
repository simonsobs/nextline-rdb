from typing import TYPE_CHECKING, Any, Optional

from nextlinegraphql.custom.strawberry import GraphQL

if TYPE_CHECKING:
    from nextline_rdb import DB


class EGraphQL(GraphQL):
    '''Extend the strawberry GraphQL app to override the `get_context` method

    This class is implemented in the way described in the strawberry document:
    https://strawberry.rocks/docs/integrations/asgi

    This class is used in tests.

    Example:

    >>> import strawberry

    >>> from nextline_rdb import DB
    >>> from nextline_rdb.schema import Query
    >>> from nextline_rdb.utils import EGraphQL

    >>> async def main():
    ...    async with DB() as db:
    ...        schema = strawberry.Schema(query=Query)
    ...        app = EGraphQL(schema).set_db(db)

    >>> import asyncio
    >>> asyncio.run(main())
    '''

    def set_db(self, db: 'DB') -> 'EGraphQL':
        self._db = db
        return self

    async def get_context(self, request, response=None) -> Optional[Any]:
        return {'request': request, 'response': response, 'db': self._db}
