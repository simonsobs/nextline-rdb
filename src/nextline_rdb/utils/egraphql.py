from typing import TYPE_CHECKING, Any, Optional

from nextlinegraphql.custom.strawberry import GraphQL

if TYPE_CHECKING:
    from nextline_rdb import AsyncDB


class EGraphQL(GraphQL):
    '''Extend the strawberry GraphQL app to override the `get_context` method

    https://strawberry.rocks/docs/integrations/asgi
    '''

    def set_db(self, db: 'AsyncDB') -> 'EGraphQL':
        self._db = db
        return self

    async def get_context(self, request, response=None) -> Optional[Any]:
        return {'request': request, 'response': response, 'db': self._db}
