from typing import Optional

from hypothesis import strategies as st

from nextline_rdb.utils.strategies import st_python_scripts

from .. import Script


def st_model_script(current: Optional[bool] = None) -> st.SearchStrategy[Script]:
    st_current = st.just(current) if current is not None else st.booleans()
    return st.builds(Script, current=st_current, script=st_python_scripts())
