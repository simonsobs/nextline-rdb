from hypothesis import given
from hypothesis import strategies as st

from nextline_rdb.db import DB
from nextline_rdb.utils import class_name_and_primary_keys_of, load_all
from nextline_rdb.utils.strategies import st_ranges

from ... import Model, Script
from .. import st_model_script_list


@given(st.data())
async def test_options(data: st.DataObject) -> None:
    min_size, max_size = data.draw(
        st_ranges(
            st_=st.integers,
            min_start=0,
            max_end=5,
            allow_start_none=False,
            allow_end_none=False,
        )
    )
    assert isinstance(min_size, int)
    assert isinstance(max_size, int)

    scripts = data.draw(st_model_script_list(min_size=min_size, max_size=max_size))

    assert min_size <= len(scripts) <= max_size

    current_script = {script for script in scripts if script.current}
    assert len(current_script) <= 1


@given(scripts=st_model_script_list(min_size=0, max_size=3))
async def test_db(scripts: list[Script]) -> None:
    async with DB(use_migration=False, model_base_class=Model) as db:
        async with db.session.begin() as session:
            session.add_all(scripts)
            added = list(session.new)
            assert set(scripts) <= set(added)
        added = sorted(added, key=class_name_and_primary_keys_of)
        repr_added = [repr(m) for m in added]

        async with db.session() as session:
            loaded = await load_all(session, Model)
            repr_loaded = [repr(m) for m in loaded]

    assert repr_added == repr_loaded
