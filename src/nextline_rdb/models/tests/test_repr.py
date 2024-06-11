import datetime
from typing import TypeVar

from hypothesis import Phase, given, settings

from nextline_rdb.db import DB
from nextline_rdb.utils import class_name_and_primary_keys_of, load_all

from .. import CurrentScript, Model, Prompt, Run, Script, Stdout, Trace, TraceCall
from ..strategies import (
    st_model_prompt,
    st_model_run,
    st_model_script,
    st_model_stdout,
    st_model_trace,
    st_model_trace_call,
)

T = TypeVar('T', bound=Model)

assert datetime, CurrentScript  # For eval()


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(instance=st_model_run())
async def test_run(instance: Run) -> None:
    await assert_repr(instance, Run)


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(instance=st_model_script())
async def test_script(instance: Script) -> None:
    await assert_repr(instance, Script)


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(instance=st_model_trace())
async def test_trace(instance: Trace) -> None:
    await assert_repr(instance, Trace)


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(instance=st_model_trace_call())
async def test_trace_call(instance: TraceCall) -> None:
    await assert_repr(instance, TraceCall)


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(instance=st_model_prompt())
async def test_prompt(instance: Prompt) -> None:
    await assert_repr(instance, Prompt)


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(instance=st_model_stdout())
async def test_stdout(instance: Stdout) -> None:
    await assert_repr(instance, Stdout)


async def assert_repr(instance: T, model: type[T]) -> None:
    '''Confirm that the repr is evaluated to reconstruct the instance.'''

    async with DB(use_migration=False, model_base_class=Model) as db:
        async with db.session.begin() as session:
            session.add(instance)
            added = list(session.new)  # Includes related instances
        added = sorted(added, key=class_name_and_primary_keys_of)
        repr_added = repr(added)

        async with db.session() as session:
            loaded = await load_all(session, Model)
        repr_loaded = repr(loaded)

        assert repr_added == repr_loaded

        reconstructed = eval(repr_loaded)
        assert isinstance(reconstructed, list)
        assert any(isinstance(item, model) for item in reconstructed)

        assert repr_loaded == repr(reconstructed)
