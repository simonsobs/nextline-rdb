from __future__ import annotations

import datetime
from typing import Optional, Type, TypeVar

import strawberry
from sqlalchemy import inspect, select
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.selectable import Select
from strawberry.types import Info

from nextline_rdb import models as db_models
from nextline_rdb.pagination import Sort, SortField

from .pagination import Connection, load_connection


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
    return await query_connection(
        info, sort, before, after, first, last, Model, NodeType
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
    return await query_connection(
        info, sort, before, after, first, last, Model, NodeType
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
    return await query_connection(
        info, sort, before, after, first, last, Model, NodeType
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
    return await query_connection(
        info, sort, before, after, first, last, Model, NodeType
    )


_M = TypeVar('_M', bound=DeclarativeBase)  # Model
_N = TypeVar("_N")  # Node


async def query_connection(
    info: Info,
    sort: Optional[Sort],
    before: Optional[str],
    after: Optional[str],
    first: Optional[int],
    last: Optional[int],
    Model: Type[_M],
    NodeType: Type[_N],
) -> Connection[_N]:
    id_field = inspect(Model).primary_key[0].name
    # TODO: handle multiple primary keys

    db = info.context['db']
    create_node_from_model = NodeType.from_model  # type: ignore

    return await load_connection(
        db,
        Model,
        id_field,
        create_node_from_model,
        sort=sort,
        before=before,
        after=after,
        first=first,
        last=last,
    )


@strawberry.type
class RunHistory:
    _model: strawberry.Private[db_models.Run]
    id: int
    run_no: int
    state: Optional[str]
    started_at: Optional[datetime.datetime]
    ended_at: Optional[datetime.datetime]
    script: Optional[str]
    exception: Optional[str]

    # traces: Connection[TraceHistory] = strawberry.field(
    #     resolver=query_connection_trace
    # )
    # prompts: Connection[PromptHistory] = strawberry.field(
    #     resolver=query_connection_prompt
    # )
    # stdouts: Connection[StdoutHistory] = strawberry.field(
    #     resolver=query_connection_stdout
    # )

    @strawberry.field
    def traces(self) -> list["TraceHistory"]:
        return [TraceHistory.from_model(m) for m in self._model.traces]  # type: ignore

    @strawberry.field
    def prompts(self) -> list["PromptHistory"]:
        return [PromptHistory.from_model(m) for m in self._model.prompts]  # type: ignore

    @strawberry.field
    def stdouts(self) -> list["StdoutHistory"]:
        return [StdoutHistory.from_model(m) for m in self._model.stdouts]  # type: ignore

    @classmethod
    def from_model(cls: Type["RunHistory"], model: db_models.Run):
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
class TraceHistory:
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
    def run(self) -> RunHistory:
        return RunHistory.from_model(self._model.run)

    # prompts: Connection[PromptHistory] = strawberry.field(
    #     resolver=query_connection_prompt
    # )

    # stdouts: Connection[StdoutHistory] = strawberry.field(
    #     resolver=query_connection_stdout
    # )

    @strawberry.field
    def prompts(self) -> list["PromptHistory"]:
        return [PromptHistory.from_model(m) for m in self._model.prompts]  # type: ignore

    @strawberry.field
    def stdouts(self) -> list["StdoutHistory"]:
        return [StdoutHistory.from_model(m) for m in self._model.stdouts]  # type: ignore

    @classmethod
    def from_model(cls: Type[TraceHistory], model: db_models.Trace):
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
class PromptHistory:
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
    def run(self) -> RunHistory:
        return RunHistory.from_model(self._model.run)

    @strawberry.field
    def trace(self) -> TraceHistory:
        return TraceHistory.from_model(self._model.trace)

    @classmethod
    def from_model(cls: Type[PromptHistory], model: db_models.Prompt):
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
class StdoutHistory:
    _model: strawberry.Private[db_models.Stdout]
    id: int
    run_no: int
    trace_no: int
    text: Optional[str] = None
    written_at: Optional[datetime.datetime] = None

    @strawberry.field
    def run(self) -> RunHistory:
        return RunHistory.from_model(self._model.run)

    @strawberry.field
    def trace(self) -> TraceHistory:
        return TraceHistory.from_model(self._model.trace)

    @classmethod
    def from_model(cls: Type[StdoutHistory], model: db_models.Stdout):
        return cls(
            _model=model,
            id=model.id,
            run_no=model.run_no,
            trace_no=model.trace_no,
            text=model.text,
            written_at=model.written_at,
        )
