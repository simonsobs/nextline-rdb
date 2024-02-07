from hypothesis import given
from hypothesis import strategies as st

from nextline_rdb.db import DB
from nextline_rdb.utils import class_name_and_primary_keys_of, load_all
from nextline_rdb.utils.strategies import st_ranges

from ... import Model
from .. import st_model_instance_list


@given(st.data())
async def test_options(data: st.DataObject) -> None:
    # Generate options of the strategy to be tested
    min_size, max_size = data.draw(
        st_ranges(
            st_=st.integers,
            min_start=0,
            max_end=8,
            allow_start_none=False,
            allow_end_none=False,
        )
    )
    assert isinstance(min_size, int)
    assert isinstance(max_size, int)

    # Call the strategy to be tested
    instances = data.draw(st_model_instance_list(min_size=min_size, max_size=max_size))

    # Assert the generated values
    assert min_size <= len(instances) <= max_size


@given(instances=st_model_instance_list(min_size=0, max_size=5))
async def test_db(instances: list[Model]) -> None:
    async with DB(use_migration=False, model_base_class=Model) as db:
        async with db.session.begin() as session:
            session.add_all(instances)
            added = list(session.new)
            assert set(instances) <= set(added)
        added = sorted(added, key=class_name_and_primary_keys_of)
        repr_added = [repr(m) for m in added]

        async with db.session() as session:
            loaded = await load_all(session, Model)
            repr_loaded = [repr(m) for m in loaded]

    assert repr_added == repr_loaded
