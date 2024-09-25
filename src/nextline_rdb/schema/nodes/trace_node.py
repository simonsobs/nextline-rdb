import datetime
from typing import TYPE_CHECKING, Annotated, Optional, cast

import strawberry
from sqlalchemy import select
from strawberry.types import Info

from nextline_rdb import models as db_models
from nextline_rdb.db import DB
from nextline_rdb.models import Prompt, Stdout
from nextline_rdb.pagination import SortField

from ..pagination import Connection, load_connection

if TYPE_CHECKING:
    from .prompt_node import PromptNode
    from .run_node import RunNode
    from .stdout_node import StdoutNode


async def _resolve_prompts(
    info: Info,
    root: 'TraceNode',
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> 'Connection[PromptNode]':
    from .prompt_node import PromptNode

    sort = [SortField('prompt_no')]
    select_model = select(Prompt).where(Prompt.trace_id == root._model.id)
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
    root: 'TraceNode',
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> 'Connection[StdoutNode]':
    from .stdout_node import StdoutNode

    sort = [SortField('written_at')]
    select_model = select(Stdout).where(Stdout.trace_id == root._model.id)
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
    def run(self) -> Annotated['RunNode', strawberry.lazy('.run_node')]:
        from .run_node import RunNode

        return RunNode.from_model(self._model.run)

    prompts: Connection[Annotated['PromptNode', strawberry.lazy('.prompt_node')]] = (
        strawberry.field(resolver=_resolve_prompts)
    )

    stdouts: Connection[Annotated['StdoutNode', strawberry.lazy('.stdout_node')]] = (
        strawberry.field(resolver=_resolve_stdouts)
    )

    @classmethod
    def from_model(cls: type['TraceNode'], model: db_models.Trace) -> 'TraceNode':
        return cls(
            _model=model,
            id=model.id,
            run_no=model.run.run_no,
            trace_no=model.trace_no,
            state=model.state,
            thread_no=model.thread_no,
            started_at=model.started_at,
            task_no=model.task_no,
            ended_at=model.ended_at,
        )
