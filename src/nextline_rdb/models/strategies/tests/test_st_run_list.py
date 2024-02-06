from hypothesis import given
from hypothesis import strategies as st

from nextline_rdb.db import DB
from nextline_rdb.utils import class_name_and_primary_keys_of, load_all
from nextline_rdb.utils.strategies import st_ranges

from ... import Model, Run
from .. import st_model_run_list


@given(st.data())
async def test_options(data: st.DataObject) -> None:
    # Generate options of the strategy to be tested
    generate_traces = data.draw(st.booleans())
    min_size, max_size = data.draw(
        st_ranges(
            st_=st.integers,
            min_start=0,
            max_end=4,
            allow_start_none=False,
            allow_end_none=False,
        )
    )
    assert isinstance(min_size, int)
    assert isinstance(max_size, int)

    # Call the strategy to be tested
    runs = data.draw(
        st_model_run_list(
            generate_traces=generate_traces, min_size=min_size, max_size=max_size
        )
    )

    # Assert the generated values
    assert min_size <= len(runs) <= max_size
    run_nos = [run.run_no for run in runs]
    assert run_nos == sorted(run_nos)

    traces = [trace for run in runs for trace in run.traces]
    prompts = [prompt for run in runs for prompt in run.prompts]
    stdouts = [stdout for run in runs for stdout in run.stdouts]

    if generate_traces is False:
        assert not traces
        assert not prompts
        assert not stdouts

    started_ats = [run.started_at for run in runs if run.started_at]
    assert started_ats == sorted(started_ats)

    current_script = {run.script for run in runs if run.script and run.script.current}
    assert len(current_script) <= 1


@given(runs=st_model_run_list(generate_traces=True, min_size=0, max_size=3))
async def test_db(runs: list[Run]) -> None:
    async with DB(use_migration=False, model_base_class=Model) as db:
        async with db.session.begin() as session:
            session.add_all(runs)
            added = list(session.new)
            assert set(runs) <= set(added)
        added = sorted(added, key=class_name_and_primary_keys_of)
        repr_added = [repr(m) for m in added]

        async with db.session() as session:
            loaded = await load_all(session, Model)
            repr_loaded = [repr(m) for m in loaded]

    assert repr_added == repr_loaded
