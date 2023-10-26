from hypothesis import strategies as st

from nextline_rdb.models import Run


@st.composite
def st_model_run(draw: st.DrawFn):
    run_no = draw(st.integers(min_value=1, max_value=2_147_483_647))
    state = draw(st.one_of(st.none(), st.text()))
    started_at = draw(st.one_of(st.none(), st.datetimes()))
    ended_at = draw(st.one_of(st.none(), st.datetimes()))
    script = draw(st.one_of(st.none(), st.text()))
    exception = draw(st.one_of(st.none(), st.text()))
    model = Run(
        run_no=run_no,
        state=state,
        started_at=started_at,
        ended_at=ended_at,
        script=script,
        exception=exception,
    )
    return model
