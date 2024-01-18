from typing import Optional, cast

import strawberry
from sqlalchemy import select
from strawberry.types import Info

from nextline_rdb.db import DB
from nextline_rdb.models import Run

from . import types
from .pagination import Connection


async def query_run(
    info: Info, id: Optional[int] = None, run_no: Optional[int] = None
) -> types.RunHistory | None:
    db = cast(DB, info.context['db'])
    async with db.session() as session:
        stmt = select(Run)
        if id is not None:
            stmt = stmt.filter(Run.id == id)
        else:
            stmt = stmt.filter(Run.run_no == run_no)
        run = (await session.execute(stmt)).scalar_one_or_none()
    return types.RunHistory.from_model(run) if run else None


@strawberry.type
class QueryRDB:
    runs: Connection[types.RunHistory] = strawberry.field(
        resolver=types.query_connection_run
    )
    traces: Connection[types.TraceHistory] = strawberry.field(
        resolver=types.query_connection_trace
    )
    prompts: Connection[types.PromptHistory] = strawberry.field(
        resolver=types.query_connection_prompt
    )
    stdouts: Connection[types.StdoutHistory] = strawberry.field(
        resolver=types.query_connection_stdout
    )
    run: types.RunHistory | None = strawberry.field(resolver=query_run)


@strawberry.type
class Query:
    @strawberry.field
    async def history(self) -> QueryRDB:
        # TODO: Remove this method.
        return QueryRDB()

    @strawberry.field
    async def rdb(self) -> QueryRDB:
        return QueryRDB()
