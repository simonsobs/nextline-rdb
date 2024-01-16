import base64
from collections.abc import Callable
from functools import partial
from typing import Optional, Type, TypeVar

from nextline_rdb import models as db_models
from nextline_rdb.db import DB
from nextline_rdb.pagination import load_models

from .connection import Connection, Edge, query_connection

_T = TypeVar('_T')


def encode_id(id: int) -> str:
    return base64.b64encode(f'{id}'.encode()).decode()


def decode_id(cursor: str) -> int:
    return int(base64.b64decode(cursor).decode())


async def load_connection(
    db: DB,
    Model: Type[db_models.Model],
    id_field: str,
    create_node_from_model: Callable[..., _T],
    *,
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> Connection[_T]:
    query_edges = partial(
        load_edges,
        db=db,
        Model=Model,
        id_field=id_field,
        create_node_from_model=create_node_from_model,
    )

    return await query_connection(
        query_edges,
        before,
        after,
        first,
        last,
    )


async def load_edges(
    db: DB,
    Model: Type[db_models.Model],
    id_field: str,
    create_node_from_model: Callable[..., _T],
    *,
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> list[Edge[_T]]:
    async with db.session() as session:
        models = await load_models(
            session,
            Model,
            id_field,
            before=before if before is None else decode_id(before),
            after=after if after is None else decode_id(after),
            first=first,
            last=last,
        )

    nodes = [create_node_from_model(m) for m in models]

    edges = [Edge(node=n, cursor=encode_id(getattr(n, id_field))) for n in nodes]

    return edges
