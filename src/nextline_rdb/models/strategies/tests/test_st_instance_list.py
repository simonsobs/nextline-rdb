from typing import Optional, TypedDict

from hypothesis import Phase, given, settings
from hypothesis import strategies as st

from nextline_rdb.db import DB
from nextline_rdb.utils import class_name_and_primary_keys_of, load_all
from nextline_test_utils import safe_compare as sc
from nextline_test_utils.strategies import st_ranges

from ... import Model, Run
from .. import st_model_instance_list


class StModelInstanceListKwargs(TypedDict, total=False):
    min_size: int
    max_size: Optional[int]
    allow_run_started_at_none: bool


@st.composite
def st_st_model_instance_list_kwargs(draw: st.DrawFn) -> StModelInstanceListKwargs:
    kwargs = StModelInstanceListKwargs()

    if draw(st.booleans()):
        min_size, max_size = draw(
            st_ranges(
                st.integers,
                min_start=0,
                max_end=8,
                allow_start_none=False,
                allow_end_none=False,
            )
        )
        assert isinstance(min_size, int)
        kwargs['min_size'] = min_size
        kwargs['max_size'] = max_size

    if draw(st.booleans()):
        kwargs['allow_run_started_at_none'] = draw(st.booleans())

    return kwargs


@given(kwargs=st_st_model_instance_list_kwargs())
def test_st_model_instance_list_kwargs(kwargs: StModelInstanceListKwargs) -> None:
    assert sc(kwargs.get('min_size')) <= sc(kwargs.get('max_size'))


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(st.data())
async def test_options(data: st.DataObject) -> None:
    # Generate options of the strategy to be tested
    kwargs = data.draw(st_st_model_instance_list_kwargs())

    # Call the strategy to be tested
    instances = data.draw(st_model_instance_list(**kwargs))

    # Assert the generated values
    min_size = kwargs.get('min_size', 0)
    max_size = kwargs.get('max_size')
    allow_run_started_at_none = kwargs.get('allow_run_started_at_none', True)

    assert min_size <= len(instances) <= sc(max_size)

    if not allow_run_started_at_none:
        runs = [instance for instance in instances if isinstance(instance, Run)]
        assert all(run.started_at is not None for run in runs)


@settings(phases=(Phase.generate,))  # Avoid shrinking
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
