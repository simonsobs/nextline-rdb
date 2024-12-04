from collections.abc import Iterable

from nextline_rdb.db import DB
from nextline_rdb.utils import class_name_and_primary_keys_of, load_all

from ... import Model


async def assert_model_persistence(instances: Iterable[Model]) -> None:
    '''Save and load the model instances and verify that they are the same.'''
    instances = list(instances)
    async with DB(use_migration=False, model_base_class=Model) as db:
        # Save all objects to the database
        async with db.session.begin() as session:
            session.add_all(instances)
            added = list(session.new)  # Associated objects are also included
            assert set(instances) <= set(added)
        added = sorted(added, key=class_name_and_primary_keys_of)
        repr_added = [repr(m) for m in added]

        # Load all objects from the database
        async with db.session() as session:
            loaded = await load_all(session, Model)
            repr_loaded = [repr(m) for m in loaded]

    # Compare the saved and loaded objects
    assert repr_added == repr_loaded
