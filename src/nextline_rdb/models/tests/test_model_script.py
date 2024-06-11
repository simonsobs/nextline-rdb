import pytest
from sqlalchemy.exc import IntegrityError

from nextline_rdb.db import DB

from .. import CurrentScript, Model, Script


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
