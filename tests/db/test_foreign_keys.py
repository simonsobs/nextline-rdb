import pytest
from sqlalchemy.exc import IntegrityError

from nextline_rdb.db import DB

from .models import Bar, Model


async def test_foreign_key_constraints() -> None:
    '''Assert that foreign key constraints are enabled.

    The foreign key constraints are not enabled by default in SQLite.

    - https://www.sqlite.org/foreignkeys.html
    - https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#foreign-key-support

    This test tries to insert a row with a foreign key that does not exist and confirms
    that an IntegrityError is raised.

    This test is copied from c5backup:
    https://github.com/simonsobs/c5backup/blob/v0.3.0/tests/test_db.py#L48
    '''
    async with DB(model_base_class=Model, use_migration=False) as db:
        async with db.session() as session:
            bar = Bar(foo_id=1)
            session.add(bar)

            with pytest.raises(IntegrityError, match=r'(?i)foreign.*key.*constraint'):
                await session.commit()
