from hypothesis import Phase, given, settings
from hypothesis import strategies as st

from nextline_rdb.db import DB
from nextline_rdb.utils import class_name_and_primary_keys_of, load_all
from nextline_test_utils import safe_compare as sc
from nextline_test_utils.strategies import (
    st_datetimes,
    st_graphql_ints,
    st_none_or,
    st_ranges,
)

from ... import Model, Run
from .. import st_model_run, st_model_script


@settings(phases=(Phase.generate,))
@given(st.data())
async def test_options(data: st.DataObject) -> None:
    # Generate options of the strategy to be tested
    run_no = data.draw(st_none_or(st_graphql_ints(min_value=1)))
    if run_no is None:
        min_run_no, max_run_no = data.draw(st_ranges(st_=st_graphql_ints, min_start=1))
    else:
        min_run_no, max_run_no = None, None

    min_started_at, max_started_at = data.draw(st_ranges(st_=st_datetimes))
    min_ended_at, max_ended_at = data.draw(
        st_ranges(st_=st_datetimes, min_start=min_started_at)
    )

    allow_started_at_none = data.draw(st.booleans())

    script = data.draw(st_none_or(st_model_script()))
    generate_script = data.draw(st.booleans())

    generate_traces = data.draw(st.booleans())

    # Call the strategy to be tested
    run = data.draw(
        st_model_run(
            run_no=run_no,
            min_run_no=min_run_no,
            max_run_no=max_run_no,
            min_started_at=min_started_at,
            max_started_at=max_started_at,
            min_ended_at=min_ended_at,
            max_ended_at=max_ended_at,
            script=script,
            allow_started_at_none=allow_started_at_none,
            generate_script=generate_script,
            generate_traces=generate_traces,
        )
    )

    # Assert the generated values
    if run_no is not None:
        assert run.run_no == run_no
    else:
        assert sc(min_run_no) <= run.run_no <= sc(max_run_no)

    if not allow_started_at_none:
        assert run.started_at is not None

    assert sc(min_started_at) <= sc(run.started_at) <= sc(max_started_at)
    assert sc(min_ended_at) <= sc(run.ended_at) <= sc(max_ended_at)
    assert sc(run.started_at) <= sc(run.ended_at)

    if not run.started_at:
        assert not run.ended_at

    if script is not None:
        assert run.script == script
    elif not generate_script:
        assert not run.script

    traces = run.traces
    trace_calls = run.trace_calls
    prompts = run.prompts
    stdouts = run.stdouts
    if generate_traces:
        assert traces
        assert trace_calls
        assert prompts
        assert stdouts
    else:
        assert not traces
        assert not trace_calls
        assert not prompts
        assert not stdouts


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(run=st_model_run())
async def test_db(run: Run) -> None:
    async with DB(use_migration=False, model_base_class=Model) as db:
        async with db.session.begin() as session:
            session.add(run)
            added = list(session.new)
            assert run in added
        added = sorted(added, key=class_name_and_primary_keys_of)
        repr_added = [repr(m) for m in added]

        async with db.session() as session:
            loaded = await load_all(session, Model)
            repr_loaded = [repr(m) for m in loaded]

    assert repr_added == repr_loaded
