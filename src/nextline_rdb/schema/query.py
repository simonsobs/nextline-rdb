from typing import Optional, cast

import strawberry
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from strawberry.types import Info

import nextline_rdb
from nextline_rdb import models as db_models
from nextline_rdb.db import DB

from .nodes import PromptNode, RunNode, SortField, StdoutNode, TraceNode
from .pagination import Connection, load_connection


async def resolve_run(
    info: Info, id: Optional[int] = None, run_no: Optional[int] = None
) -> RunNode | None:
    db = cast(DB, info.context['db'])
    async with db.session() as session:
        info.context['session'] = session
        stmt = select(db_models.Run).options(selectinload('*'))
        if id is not None:
            stmt = stmt.filter(db_models.Run.id == id)
        else:
            stmt = stmt.filter(db_models.Run.run_no == run_no)
        run = (await session.execute(stmt)).scalar_one_or_none()
    return RunNode.from_model(run) if run else None


async def resolve_runs(
    info: Info,
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> Connection[RunNode]:
    sort = [SortField('run_no', desc=True)]
    Model = db_models.Run
    NodeType = RunNode
    create_node_from_model = NodeType.from_model
    db = cast(DB, info.context['db'])
    async with db.session() as session:
        info.context['session'] = session
        return await load_connection(
            session,
            Model,
            create_node_from_model,
            sort=sort,
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
    sort = [SortField('run_no'), SortField('trace_no')]
    Model = db_models.Trace
    NodeType = TraceNode
    create_node_from_model = NodeType.from_model
    db = cast(DB, info.context['db'])
    async with db.session() as session:
        info.context['session'] = session
        return await load_connection(
            session,
            Model,
            create_node_from_model,
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
    sort = [SortField('run_no'), SortField('prompt_no')]
    Model = db_models.Prompt
    NodeType = PromptNode
    create_node_from_model = NodeType.from_model
    db = cast(DB, info.context['db'])
    async with db.session() as session:
        info.context['session'] = session
        return await load_connection(
            session,
            Model,
            create_node_from_model,
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
    sort = [SortField('run_no'), SortField('id')]
    Model = db_models.Stdout
    NodeType = StdoutNode
    create_node_from_model = NodeType.from_model
    db = cast(DB, info.context['db'])
    async with db.session() as session:
        info.context['session'] = session
        return await load_connection(
            session,
            Model,
            create_node_from_model,
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
    prompts: Connection[PromptNode] = strawberry.field(resolver=resolve_prompts)
    stdouts: Connection[StdoutNode] = strawberry.field(resolver=resolve_stdouts)
    run: RunNode | None = strawberry.field(resolver=resolve_run)
    version: str = nextline_rdb.__version__
    migration_version: str | None = strawberry.field(resolver=resolve_migration_version)


@strawberry.type
class Query:
    @strawberry.field
    async def history(self) -> QueryRDB:
        # TODO: Remove this method.
        return QueryRDB()

    @strawberry.field
    async def rdb(self) -> QueryRDB:
        return QueryRDB()
