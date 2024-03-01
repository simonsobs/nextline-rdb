import datetime
from typing import TYPE_CHECKING, Annotated, Optional

import strawberry

from nextline_rdb import models as db_models

if TYPE_CHECKING:
    from .prompt_node import PromptNode
    from .run_node import RunNode
    from .stdout_node import StdoutNode


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

    # prompts: Connection[PromptHistory] = strawberry.field(
    #     resolver=query_connection_prompt
    # )

    # stdouts: Connection[StdoutHistory] = strawberry.field(
    #     resolver=query_connection_stdout
    # )

    @strawberry.field
    def prompts(self) -> list[Annotated['PromptNode', strawberry.lazy('.prompt_node')]]:
        from .prompt_node import PromptNode

        return [PromptNode.from_model(m) for m in self._model.prompts]  # type: ignore

    @strawberry.field
    def stdouts(self) -> list[Annotated['StdoutNode', strawberry.lazy('.stdout_node')]]:
        from .stdout_node import StdoutNode

        return [StdoutNode.from_model(m) for m in self._model.stdouts]  # type: ignore

    @classmethod
    def from_model(cls: type['TraceNode'], model: db_models.Trace):
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
