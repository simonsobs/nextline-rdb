from typing import Optional, cast

import strawberry
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from strawberry.types import Info

import nextline_rdb
from nextline_rdb import models as db_models
from nextline_rdb.db import DB

from . import types
from .pagination import Connection
from .types import (
    PromptHistory,
    RunHistory,
    SortField,
    StdoutHistory,
    TraceHistory,
    query_connection,
)


async def query_run(
    info: Info, id: Optional[int] = None, run_no: Optional[int] = None
) -> types.RunHistory | None:
    db = cast(DB, info.context['db'])
    async with db.session() as session:
        info.context['session'] = session
        stmt = select(db_models.Run).options(selectinload('*'))
        if id is not None:
            stmt = stmt.filter(db_models.Run.id == id)
        else:
            stmt = stmt.filter(db_models.Run.run_no == run_no)
        run = (await session.execute(stmt)).scalar_one_or_none()
    return types.RunHistory.from_model(run) if run else None


async def query_connection_run(
    info: Info,
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> Connection[RunHistory]:
    sort = [SortField('run_no', desc=True)]
    Model = db_models.Run
    NodeType = RunHistory
    db = cast(DB, info.context['db'])
    async with db.session() as session:
        info.context['session'] = session
        return await query_connection(
            session, sort, before, after, first, last, Model, NodeType
        )


async def query_connection_trace(
    info: Info,
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> Connection[TraceHistory]:
    sort = [SortField('run_no'), SortField('trace_no')]
    Model = db_models.Trace
    NodeType = TraceHistory
    db = cast(DB, info.context['db'])
    async with db.session() as session:
        info.context['session'] = session
        return await query_connection(
            session, sort, before, after, first, last, Model, NodeType
        )


async def query_connection_prompt(
    info: Info,
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> Connection[PromptHistory]:
    sort = [SortField('run_no'), SortField('prompt_no')]
    Model = db_models.Prompt
    NodeType = PromptHistory
    db = cast(DB, info.context['db'])
    async with db.session() as session:
        info.context['session'] = session
        return await query_connection(
            session, sort, before, after, first, last, Model, NodeType
        )


async def query_connection_stdout(
    info: Info,
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> Connection[StdoutHistory]:
    sort = [SortField('run_no'), SortField('id')]
    Model = db_models.Stdout
    NodeType = StdoutHistory
    db = cast(DB, info.context['db'])
    async with db.session() as session:
        info.context['session'] = session
        return await query_connection(
            session, sort, before, after, first, last, Model, NodeType
        )


def query_migration_version(info: Info) -> str | None:
    db = cast(DB, info.context['db'])
    return db.migration_revision


@strawberry.type
class QueryRDB:
    runs: Connection[types.RunHistory] = strawberry.field(resolver=query_connection_run)
    traces: Connection[types.TraceHistory] = strawberry.field(
        resolver=query_connection_trace
    )
    prompts: Connection[types.PromptHistory] = strawberry.field(
        resolver=query_connection_prompt
    )
    stdouts: Connection[types.StdoutHistory] = strawberry.field(
        resolver=query_connection_stdout
    )
    run: types.RunHistory | None = strawberry.field(resolver=query_run)
    version: str = nextline_rdb.__version__
    migration_version: str | None = strawberry.field(resolver=query_migration_version)


@strawberry.type
class Query:
    @strawberry.field
    async def history(self) -> QueryRDB:
        # TODO: Remove this method.
        return QueryRDB()

    @strawberry.field
    async def rdb(self) -> QueryRDB:
        return QueryRDB()
