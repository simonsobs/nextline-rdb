from typing import TypeVar

from hypothesis import Phase, given, settings
from sqlalchemy import select

from nextline_rdb.db import DB

from .. import Model, Prompt, Run, Stdout, Trace, TraceCall
from ..strategies import st_model_run, st_model_trace, st_model_trace_call

T = TypeVar('T', bound=Model)


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(parent=st_model_run(generate_traces=True))
async def test_run(parent: Run) -> None:
    await assert_cascade(parent, Run, [Prompt, Trace, TraceCall, Stdout])


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(parent=st_model_trace(generate_trace_calls=True, generate_prompts=True))
async def test_trace(parent: Trace) -> None:
    await assert_cascade(parent, Trace, [Prompt, TraceCall])


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(parent=st_model_trace_call(generate_prompts=True))
async def test_trace_call(parent: TraceCall) -> None:
    await assert_cascade(parent, TraceCall, [Prompt])  # type: ignore


async def assert_cascade(
    parent: T, parent_type: type[T], children_types: list[type[T]]
) -> None:
    async with DB(use_migration=False, model_base_class=Model) as db:
        async with db.session.begin() as session:
            session.add(parent)

        async with db.session.begin() as session:
            select_parent = select(parent_type)
            parent = (await session.execute(select_parent)).scalar_one()
            await session.delete(parent)

        async with db.session() as session:
            for child_type in children_types:
                select_children = select(child_type)
                child = (await session.execute(select_children)).scalar_one_or_none()
                assert child is None
