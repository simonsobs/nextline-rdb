import datetime
from typing import TYPE_CHECKING, Annotated, Optional, cast

import strawberry
from sqlalchemy import select
from strawberry.types import Info

from nextline_rdb import models as db_models
from nextline_rdb.db import DB
from nextline_rdb.models import Prompt
from nextline_rdb.pagination import SortField

from ..pagination import Connection, load_connection

if TYPE_CHECKING:
    from .prompt_node import PromptNode
    from .run_node import RunNode
    from .trace_node import TraceNode


async def _resolve_prompts(
    info: Info,
    root: 'TraceCallNode',
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


@strawberry.type
class TraceCallNode:
    _model: strawberry.Private[db_models.TraceCall]
    id: int
    run_no: int
    trace_no: int
    trace_call_no: int
    thread_no: int
    event: str
    started_at: datetime.datetime
    file_name: Optional[str] = None
    line_no: Optional[int] = None
    task_no: Optional[int]
    ended_at: Optional[datetime.datetime]

    @strawberry.field
    def run(self) -> Annotated['RunNode', strawberry.lazy('.run_node')]:
        from .run_node import RunNode

        return RunNode.from_model(self._model.run)

    @strawberry.field
    def trace(self) -> Annotated['TraceNode', strawberry.lazy('.trace_node')]:
        from .trace_node import TraceNode

        return TraceNode.from_model(self._model.trace)

    prompts: Connection[Annotated['PromptNode', strawberry.lazy('.prompt_node')]] = (
        strawberry.field(resolver=_resolve_prompts)
    )

    @classmethod
    def from_model(
        cls: type['TraceCallNode'], model: db_models.TraceCall
    ) -> 'TraceCallNode':
        return cls(
            _model=model,
            id=model.id,
            run_no=model.run.run_no,
            trace_no=model.trace.trace_no,
            trace_call_no=model.trace_call_no,
            thread_no=model.trace.thread_no,
            event=model.event,
            started_at=model.started_at,
            file_name=model.file_name,
            line_no=model.line_no,
            task_no=model.trace.task_no,
            ended_at=model.ended_at,
        )
