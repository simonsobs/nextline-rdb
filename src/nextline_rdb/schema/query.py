from datetime import datetime
from typing import Optional, cast

import strawberry
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from strawberry.types import Info

import nextline_rdb
from nextline_rdb.db import DB
from nextline_rdb.models import Prompt, Run, Stdout, Trace, TraceCall
from nextline_rdb.pagination import SortField
from nextline_rdb.utils import to_naive_utc

from .nodes import PromptNode, RunNode, StdoutNode, TraceCallNode, TraceNode
from .pagination import Connection, load_connection


async def resolve_run(
    info: Info, id: Optional[int] = None, run_no: Optional[int] = None
) -> RunNode | None:
    db = cast(DB, info.context['db'])
    async with db.session() as session:
        # stmt = select(Run).options(selectinload('*'))
        stmt = select(Run).options(selectinload(Run.script))
        if id is not None:
            stmt = stmt.filter(Run.id == id)
        else:
            stmt = stmt.filter(Run.run_no == run_no)
        run = (await session.execute(stmt)).scalar_one_or_none()
    return RunNode.from_model(run) if run else None


@strawberry.input
class RunFilter:
    started_after: Optional[datetime] = None
    started_before: Optional[datetime] = None
    ended_after: Optional[datetime] = None
    ended_before: Optional[datetime] = None


async def resolve_runs(
    info: Info,
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
    filter: Optional[RunFilter] = None,
) -> Connection[RunNode]:
    sort = [SortField('run_no', desc=True)]
    db = cast(DB, info.context['db'])

    stmt = select(Run)

    if filter:
        if filter.started_after:
            started_after = to_naive_utc(filter.started_after)
            stmt = stmt.where(Run.started_at >= started_after)
        if filter.started_before:
            started_before = to_naive_utc(filter.started_before)
            stmt = stmt.where(Run.started_at < started_before)
        if filter.ended_after:
            ended_after = to_naive_utc(filter.ended_after)
            stmt = stmt.where(Run.ended_at >= ended_after)
        if filter.ended_before:
            ended_before = to_naive_utc(filter.ended_before)
            stmt = stmt.where(Run.ended_at < ended_before)

    async with db.session() as session:
        return await load_connection(
            session,
            Run,
            create_node_from_model=RunNode.from_model,
            sort=sort,
            select_model=stmt,
            before=before,
            after=after,
            first=first,
            last=last,
        )


async def resolve_traces(
    info: Info,
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> Connection[TraceNode]:
    sort = [SortField('run_id'), SortField('trace_no')]
    db = cast(DB, info.context['db'])
    async with db.session() as session:
        return await load_connection(
            session,
            Trace,
            create_node_from_model=TraceNode.from_model,
            sort=sort,
            before=before,
            after=after,
            first=first,
            last=last,
        )


async def resolve_trace_calls(
    info: Info,
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> Connection[TraceCallNode]:
    sort = [SortField('run_id'), SortField('trace_call_no')]
    db = cast(DB, info.context['db'])
    async with db.session() as session:
        return await load_connection(
            session,
            TraceCall,
            create_node_from_model=TraceCallNode.from_model,
            sort=sort,
            before=before,
            after=after,
            first=first,
            last=last,
        )


async def resolve_prompts(
    info: Info,
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> Connection[PromptNode]:
    sort = [SortField('run_id'), SortField('prompt_no')]
    db = cast(DB, info.context['db'])
    async with db.session() as session:
        return await load_connection(
            session,
            Prompt,
            create_node_from_model=PromptNode.from_model,
            sort=sort,
            before=before,
            after=after,
            first=first,
            last=last,
        )


async def resolve_stdouts(
    info: Info,
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> Connection[StdoutNode]:
    sort = [SortField('run_id'), SortField('id')]
    db = cast(DB, info.context['db'])
    async with db.session() as session:
        return await load_connection(
            session,
            Stdout,
            create_node_from_model=StdoutNode.from_model,
            sort=sort,
            before=before,
            after=after,
            first=first,
            last=last,
        )


def resolve_migration_version(info: Info) -> str | None:
    db = cast(DB, info.context['db'])
    return db.migration_revision


@strawberry.type
class QueryRDB:
    runs: Connection[RunNode] = strawberry.field(resolver=resolve_runs)
    traces: Connection[TraceNode] = strawberry.field(resolver=resolve_traces)
    trace_calls: Connection[TraceCallNode] = strawberry.field(
        resolver=resolve_trace_calls
    )
    prompts: Connection[PromptNode] = strawberry.field(resolver=resolve_prompts)
    stdouts: Connection[StdoutNode] = strawberry.field(resolver=resolve_stdouts)
    run: RunNode | None = strawberry.field(resolver=resolve_run)
    version: str = nextline_rdb.__version__
    migration_version: str | None = strawberry.field(resolver=resolve_migration_version)


@strawberry.type
class Query:
    @strawberry.field(
        deprecation_reason=(
            "This field will be removed in a future version."
            "Use `rdb` field instead."
            "This field is an old name for `rdb` and now is an alias for it."
        )
    )
    async def history(self) -> QueryRDB:  # pragma: no cover
        # TODO: Remove this method.
        return QueryRDB()

    @strawberry.field
    async def rdb(self) -> QueryRDB:
        return QueryRDB()
