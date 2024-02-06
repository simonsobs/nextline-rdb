import pytest
from hypothesis import given
from sqlalchemy.exc import IntegrityError

from nextline_rdb.db import DB
from nextline_rdb.utils import class_name_and_primary_keys_of, load_all

from .. import CurrentScript, Model, Script
from ..strategies import st_model_script


@given(script=st_model_script())
async def test_repr(script: Script) -> None:
    async with DB(use_migration=False, model_base_class=Model) as db:
        async with db.session.begin() as session:
            session.add(script)
            added = list(session.new)
        added = sorted(added, key=class_name_and_primary_keys_of)
        repr_added = repr(added)

        async with db.session() as session:
            loaded = await load_all(session, Model)
            repr_loaded = repr(loaded)

            assert repr_added == repr_loaded
            assert CurrentScript  # type: ignore[truthy-function]
            assert repr_loaded == repr(eval(repr_loaded))


async def test_at_most_one_current_script() -> None:
    async with DB(use_migration=False, model_base_class=Model) as db:
        async with db.session() as session:
            current_script = CurrentScript(script=Script(script=''))
            session.add(current_script)
            await session.commit()

            current_script = CurrentScript(script=Script(script=''))
            session.add(current_script)
            with pytest.raises(IntegrityError):
                await session.commit()
