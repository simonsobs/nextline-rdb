from hypothesis import given
from hypothesis import strategies as st

from nextline_rdb.db import DB
from nextline_rdb.utils import class_name_and_primary_keys_of, load_all
from nextline_rdb.utils.strategies import st_none_or

from ... import Model, Script
from .. import st_model_script


@given(st.data())
async def test_options(data: st.DataObject) -> None:
    current = data.draw(st_none_or(st.booleans()))
    script = data.draw(st_model_script(current=current))
    if current is not None:
        assert script.current == current
    compile(script.script, '<string>', 'exec')


@given(script=st_model_script())
async def test_db(script: Script) -> None:
    async with DB(use_migration=False, model_base_class=Model) as db:
        async with db.session.begin() as session:
            session.add(script)
            added = list(session.new)
            assert script in added
        added = sorted(added, key=class_name_and_primary_keys_of)
        repr_added = [repr(m) for m in added]

        async with db.session() as session:
            loaded = await load_all(session, Model)
            repr_loaded = [repr(m) for m in loaded]

    assert repr_added == repr_loaded
