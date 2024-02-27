import base64
from collections.abc import Callable
from functools import partial
from typing import Optional, Type, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.selectable import Select

from nextline_rdb import models as db_models
from nextline_rdb.db import DB
from nextline_rdb.pagination import Sort, load_models

from .connection import Connection, Edge, query_connection

_M = TypeVar('_M', bound=DeclarativeBase)  # Model
_N = TypeVar('_N')  # Node


def encode_id(id: int) -> str:
    return base64.b64encode(f'{id}'.encode()).decode()


def decode_id(cursor: str) -> int:
    return int(base64.b64decode(cursor).decode())


async def load_connection(
    db: DB,
    Model: Type[_M],
    id_field: str,
    create_node_from_model: Callable[..., _M],
    *,
    select_model: Optional[Select[tuple[_M]]] = None,
    sort: Optional[Sort] = None,
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> Connection[_N]:
    async with db.session() as session:
        query_edges = partial(
            load_edges,
            session=session,
            Model=Model,
            id_field=id_field,
            create_node_from_model=create_node_from_model,
            select_model=select_model,
            sort=sort,
        )

        query_total_count = partial(load_total_count, session=session, Model=Model)

        return await query_connection(
            query_edges,
            query_total_count,
            before,
            after,
            first,
            last,
        )


async def load_total_count(session: AsyncSession, Model: Type[db_models.Model]) -> int:
    stmt = select(func.count()).select_from(Model)
    total_count = (await session.execute(stmt)).scalar() or 0
    return total_count


async def load_edges(
    session: AsyncSession,
    Model: Type[_M],
    id_field: str,
    create_node_from_model: Callable[..., _N],
    *,
    select_model: Optional[Select[tuple[_M]]] = None,
    sort: Optional[Sort] = None,
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> list[Edge[_N]]:
    models = await load_models(
        session,
        Model,
        id_field,
        select_model=select_model,
        sort=sort,
        before=before if before is None else decode_id(before),
        after=after if after is None else decode_id(after),
        first=first,
        last=last,
    )

    nodes = [create_node_from_model(m) for m in models]

    edges = [Edge(node=n, cursor=encode_id(getattr(n, id_field))) for n in nodes]

    return edges
