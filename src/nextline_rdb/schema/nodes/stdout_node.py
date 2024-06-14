import datetime
from typing import TYPE_CHECKING, Annotated, Optional

import strawberry

from nextline_rdb import models as db_models

if TYPE_CHECKING:
    from .run_node import RunNode
    from .trace_node import TraceNode


@strawberry.type
class StdoutNode:
    _model: strawberry.Private[db_models.Stdout]
    id: int
    run_no: int
    trace_no: int
    text: Optional[str] = None
    written_at: Optional[datetime.datetime] = None

    @strawberry.field
    def run(self) -> Annotated['RunNode', strawberry.lazy('.run_node')]:
        from .run_node import RunNode

        return RunNode.from_model(self._model.run)

    @strawberry.field
    def trace(self) -> Annotated['TraceNode', strawberry.lazy('.trace_node')]:
        from .trace_node import TraceNode

        return TraceNode.from_model(self._model.trace)

    @classmethod
    def from_model(cls: type['StdoutNode'], model: db_models.Stdout) -> 'StdoutNode':
        return cls(
            _model=model,
            id=model.id,
            run_no=model.run.run_no,
            trace_no=model.trace.trace_no,
            text=model.text,
            written_at=model.written_at,
        )
