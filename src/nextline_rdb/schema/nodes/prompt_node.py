import datetime
from typing import TYPE_CHECKING, Annotated, Optional

import strawberry

from nextline_rdb import models as db_models

if TYPE_CHECKING:
    from .run_node import RunNode
    from .trace_node import TraceNode


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
    def run(self) -> Annotated['RunNode', strawberry.lazy('.run_node')]:
        from .run_node import RunNode

        return RunNode.from_model(self._model.run)

    @strawberry.field
    def trace(self) -> Annotated['TraceNode', strawberry.lazy('.trace_node')]:
        from .trace_node import TraceNode

        return TraceNode.from_model(self._model.trace)

    @classmethod
    def from_model(cls: type['PromptNode'], model: db_models.Prompt):
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
