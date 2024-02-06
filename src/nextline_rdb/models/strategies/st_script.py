from typing import Optional

from hypothesis import strategies as st

from nextline_rdb.utils.strategies import st_python_scripts, st_none_or

from .. import Script


def st_model_script(current: Optional[bool] = None) -> st.SearchStrategy[Script]:
    st_current = st.just(current) if current is not None else st.booleans()
    return st.builds(Script, current=st_current, script=st_python_scripts())


@st.composite
def st_model_script_list(
    draw: st.DrawFn,
    min_size: int = 0,
    max_size: Optional[int] = None,
) -> list[Script]:
    scripts = draw(
        st.lists(st_model_script(current=False), min_size=min_size, max_size=max_size)
    )
    if scripts:
        current = draw(st_none_or(st.sampled_from(scripts)))
        if current is not None:
            current.current = True
    return scripts
