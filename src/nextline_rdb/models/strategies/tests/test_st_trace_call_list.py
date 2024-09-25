from hypothesis import Phase, given, settings
from hypothesis import strategies as st
from sqlalchemy import select

from nextline_rdb.db import DB
from nextline_rdb.utils import class_name_and_primary_keys_of
from nextline_test_utils.strategies import st_none_or

from ... import Model, TraceCall
from .. import st_model_run, st_model_trace_call_list, st_model_trace_list


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(st.data())
async def test_st_model_trace_call_lists(data: st.DataObject) -> None:
    # generate_traces=False because True would generate a trace with trace_calls
    if run := data.draw(st_none_or(st_model_run(generate_traces=False))):
        data.draw(st_none_or(st_model_trace_list(run=run, min_size=0, max_size=3)))
        assert run.traces is not None

    max_size = data.draw(st.integers(min_value=0, max_value=5))

    trace_calls = data.draw(st_model_trace_call_list(run=run, max_size=max_size))

    assert len(trace_calls) <= max_size

    if trace_calls:
        runs = set(trace_call.trace.run for trace_call in trace_calls)
        assert len(runs) == 1
        assert run is None or run is runs.pop()

    async with DB(use_migration=False, model_base_class=Model) as db:
        async with db.session.begin() as session:
            session.add_all(trace_calls)

        trace_calls = sorted(trace_calls, key=class_name_and_primary_keys_of)
        expected = repr(trace_calls)

        async with db.session() as session:
            select_trace_call = select(TraceCall)
            trace_calls_ = (await session.scalars(select_trace_call)).all()
            session.expunge_all()

        trace_calls_ = sorted(trace_calls_, key=class_name_and_primary_keys_of)
        actual = repr(trace_calls_)

    assert expected == actual
