import datetime
from typing import TYPE_CHECKING, Annotated, Optional, cast

import strawberry
from sqlalchemy import select
from strawberry.types import Info

from nextline_rdb import models as db_models
from nextline_rdb.db import DB
from nextline_rdb.pagination import SortField

from ..pagination import Connection, load_connection

if TYPE_CHECKING:
    from .prompt_node import PromptNode
    from .stdout_node import StdoutNode
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

    sort = [SortField('run_no'), SortField('trace_no')]
    Model = db_models.Trace
    NodeType = TraceNode
    create_node_from_model = NodeType.from_model
    select_model = select(Model).where(Model.run_id == root._model.id)
    db = cast(DB, info.context['db'])
    async with db.session() as session:
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

    traces: Connection[
        Annotated['TraceNode', strawberry.lazy('.trace_node')]
    ] = strawberry.field(resolver=_resolve_traces)

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
    def prompts(self) -> list[Annotated['PromptNode', strawberry.lazy('.prompt_node')]]:
        from .prompt_node import PromptNode

        return [PromptNode.from_model(m) for m in self._model.prompts]  # type: ignore

    @strawberry.field
    def stdouts(self) -> list[Annotated['StdoutNode', strawberry.lazy('.stdout_node')]]:
        from .stdout_node import StdoutNode

        return [StdoutNode.from_model(m) for m in self._model.stdouts]  # type: ignore

    @classmethod
    def from_model(cls: type['RunNode'], model: db_models.Run):
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
