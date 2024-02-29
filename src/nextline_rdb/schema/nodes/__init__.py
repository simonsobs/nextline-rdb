from __future__ import annotations

import datetime
from typing import Optional, Type, TypeVar

import strawberry
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.selectable import Select
from strawberry.types import Info

from nextline_rdb import models as db_models
from nextline_rdb.pagination import Sort, SortField

from ..pagination import Connection, load_connection

_M = TypeVar('_M', bound=DeclarativeBase)  # Model
_N = TypeVar("_N")  # Node


async def query_connection(
    session: AsyncSession,
    sort: Optional[Sort],
    before: Optional[str],
    after: Optional[str],
    first: Optional[int],
    last: Optional[int],
    Model: Type[_M],
    NodeType: Type[_N],
    select_model: Optional[Select[tuple[_M]]] = None,
) -> Connection[_N]:
    create_node_from_model = NodeType.from_model  # type: ignore

    return await load_connection(
        session,
        Model,
        create_node_from_model,
        select_model=select_model,
        sort=sort,
        before=before,
        after=after,
        first=first,
        last=last,
    )


async def _query_connection_trace(
    info: Info,
    root,
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> Connection[TraceNode]:
    sort = [SortField('run_no'), SortField('trace_no')]
    Model = db_models.Trace
    NodeType = TraceNode
    ic(root._model)
    select_model = select(Model).where(Model.run == root._model)
    session = info.context['session']
    return await query_connection(
        session,
        sort,
        before,
        after,
        first,
        last,
        Model,
        NodeType,
        select_model=select_model,
    )


@strawberry.type
class RunNode:
    _model: strawberry.Private[db_models.Run]
    id: int
    run_no: int
    state: Optional[str]
    started_at: Optional[datetime.datetime]
    ended_at: Optional[datetime.datetime]
    script: Optional[str]
    exception: Optional[str]

    traces: Connection[TraceNode] = strawberry.field(resolver=_query_connection_trace)

    # prompts: Connection[PromptHistory] = strawberry.field(
    #     resolver=query_connection_prompt
    # )
    # stdouts: Connection[StdoutHistory] = strawberry.field(
    #     resolver=query_connection_stdout
    # )

    # @strawberry.field
    # def traces(self) -> list["TraceHistory"]:
    #     return [TraceHistory.from_model(m) for m in self._model.traces]  # type: ignore

    @strawberry.field
    def prompts(self) -> list["PromptNode"]:
        return [PromptNode.from_model(m) for m in self._model.prompts]  # type: ignore

    @strawberry.field
    def stdouts(self) -> list["StdoutNode"]:
        return [StdoutNode.from_model(m) for m in self._model.stdouts]  # type: ignore

    @classmethod
    def from_model(cls: Type["RunNode"], model: db_models.Run):
        script = model.script.script if model.script else None
        return cls(
            _model=model,
            id=model.id,
            run_no=model.run_no,
            state=model.state,
            started_at=model.started_at,
            ended_at=model.ended_at,
            script=script,
            exception=model.exception,
        )


@strawberry.type
class TraceNode:
    _model: strawberry.Private[db_models.Trace]
    id: int
    run_no: int
    trace_no: int
    state: str
    thread_no: int
    started_at: datetime.datetime
    task_no: Optional[int]
    ended_at: Optional[datetime.datetime]

    @strawberry.field
    def run(self) -> RunNode:
        return RunNode.from_model(self._model.run)

    # prompts: Connection[PromptHistory] = strawberry.field(
    #     resolver=query_connection_prompt
    # )

    # stdouts: Connection[StdoutHistory] = strawberry.field(
    #     resolver=query_connection_stdout
    # )

    @strawberry.field
    def prompts(self) -> list["PromptNode"]:
        return [PromptNode.from_model(m) for m in self._model.prompts]  # type: ignore

    @strawberry.field
    def stdouts(self) -> list["StdoutNode"]:
        return [StdoutNode.from_model(m) for m in self._model.stdouts]  # type: ignore

    @classmethod
    def from_model(cls: Type[TraceNode], model: db_models.Trace):
        return cls(
            _model=model,
            id=model.id,
            run_no=model.run_no,
            trace_no=model.trace_no,
            state=model.state,
            thread_no=model.thread_no,
            started_at=model.started_at,
            task_no=model.task_no,
            ended_at=model.ended_at,
        )


@strawberry.type
class PromptNode:
    _model: strawberry.Private[db_models.Prompt]
    id: int
    run_no: int
    trace_no: int
    prompt_no: int
    open: bool
    event: str
    started_at: datetime.datetime
    file_name: Optional[str] = None
    line_no: Optional[int] = None
    stdout: Optional[str] = None
    command: Optional[str] = None
    ended_at: Optional[datetime.datetime] = None

    @strawberry.field
    def run(self) -> RunNode:
        return RunNode.from_model(self._model.run)

    @strawberry.field
    def trace(self) -> TraceNode:
        return TraceNode.from_model(self._model.trace)

    @classmethod
    def from_model(cls: Type[PromptNode], model: db_models.Prompt):
        return cls(
            _model=model,
            id=model.id,
            run_no=model.run_no,
            trace_no=model.trace_no,
            prompt_no=model.prompt_no,
            open=model.open,
            event=model.event,
            started_at=model.started_at,
            file_name=model.file_name,
            line_no=model.line_no,
            stdout=model.stdout,
            command=model.command,
            ended_at=model.ended_at,
        )


@strawberry.type
class StdoutNode:
    _model: strawberry.Private[db_models.Stdout]
    id: int
    run_no: int
    trace_no: int
    text: Optional[str] = None
    written_at: Optional[datetime.datetime] = None

    @strawberry.field
    def run(self) -> RunNode:
        return RunNode.from_model(self._model.run)

    @strawberry.field
    def trace(self) -> TraceNode:
        return TraceNode.from_model(self._model.trace)

    @classmethod
    def from_model(cls: Type[StdoutNode], model: db_models.Stdout):
        return cls(
            _model=model,
            id=model.id,
            run_no=model.run_no,
            trace_no=model.trace_no,
            text=model.text,
            written_at=model.written_at,
        )
