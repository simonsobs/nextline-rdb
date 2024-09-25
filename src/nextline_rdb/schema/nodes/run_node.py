import datetime
from typing import TYPE_CHECKING, Annotated, Optional, cast

import strawberry
from sqlalchemy import select
from strawberry.types import Info

from nextline_rdb.db import DB
from nextline_rdb.models import Prompt, Run, Stdout, Trace, TraceCall
from nextline_rdb.pagination import SortField

from ..pagination import Connection, load_connection

if TYPE_CHECKING:
    from .prompt_node import PromptNode
    from .stdout_node import StdoutNode
    from .trace_call_node import TraceCallNode
    from .trace_node import TraceNode


async def _resolve_traces(
    info: Info,
    root: 'RunNode',
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> Connection['TraceNode']:
    from .trace_node import TraceNode

    sort = [SortField('trace_no')]
    select_model = select(Trace).where(Trace.run_id == root._model.id)
    db = cast(DB, info.context['db'])
    async with db.session() as session:
        return await load_connection(
            session,
            Trace,
            create_node_from_model=TraceNode.from_model,
            select_model=select_model,
            sort=sort,
            before=before,
            after=after,
            first=first,
            last=last,
        )


async def _resolve_trace_calls(
    info: Info,
    root: 'RunNode',
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> Connection['TraceCallNode']:
    from .trace_call_node import TraceCallNode

    sort = [SortField('trace_call_no')]
    select_model = select(TraceCall).where(TraceCall.run_id == root._model.id)
    db = cast(DB, info.context['db'])
    async with db.session() as session:
        return await load_connection(
            session,
            TraceCall,
            create_node_from_model=TraceCallNode.from_model,
            select_model=select_model,
            sort=sort,
            before=before,
            after=after,
            first=first,
            last=last,
        )


async def _resolve_prompts(
    info: Info,
    root: 'RunNode',
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> Connection['PromptNode']:
    from .prompt_node import PromptNode

    sort = [SortField('prompt_no')]
    select_model = select(Prompt).where(Prompt.run_id == root._model.id)
    db = cast(DB, info.context['db'])
    async with db.session() as session:
        return await load_connection(
            session,
            Prompt,
            create_node_from_model=PromptNode.from_model,
            select_model=select_model,
            sort=sort,
            before=before,
            after=after,
            first=first,
            last=last,
        )


async def _resolve_stdouts(
    info: Info,
    root: 'RunNode',
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> Connection['StdoutNode']:
    from .stdout_node import StdoutNode

    sort = [SortField('written_at')]
    select_model = select(Stdout).where(Stdout.run_id == root._model.id)
    db = cast(DB, info.context['db'])
    async with db.session() as session:
        return await load_connection(
            session,
            Stdout,
            create_node_from_model=StdoutNode.from_model,
            select_model=select_model,
            sort=sort,
            before=before,
            after=after,
            first=first,
            last=last,
        )


@strawberry.type
class RunNode:
    _model: strawberry.Private[Run]
    id: int
    run_no: int
    state: Optional[str]
    started_at: Optional[datetime.datetime]
    ended_at: Optional[datetime.datetime]
    script: Optional[str]
    exception: Optional[str]

    traces: Connection[Annotated['TraceNode', strawberry.lazy('.trace_node')]] = (
        strawberry.field(resolver=_resolve_traces)
    )

    trace_calls: Connection[
        Annotated['TraceCallNode', strawberry.lazy('.trace_call_node')]
    ] = strawberry.field(resolver=_resolve_trace_calls)

    prompts: Connection[Annotated['PromptNode', strawberry.lazy('.prompt_node')]] = (
        strawberry.field(resolver=_resolve_prompts)
    )

    stdouts: Connection[Annotated['StdoutNode', strawberry.lazy('.stdout_node')]] = (
        strawberry.field(resolver=_resolve_stdouts)
    )

    @classmethod
    def from_model(cls: type['RunNode'], model: Run) -> 'RunNode':
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
