from asyncio import to_thread

from alembic import command
from hypothesis import given, note
from hypothesis import strategies as st

from nextline_rdb.alembic.models import rev_f9a742bb2297 as models_old
from nextline_rdb.alembic.models.rev_f9a742bb2297.strategies import st_model_script
from nextline_rdb.db import DB
from nextline_rdb.utils import load_all

from .conftest import AlembicConfigFactory

REVISION_START = 'f9a742bb2297'
REVISION_STAGE_ONE = 'c72fa3ee6a1a'
REVISION_NEW = '4dc6a93dfed8'


@given(scripts=st.lists(st_model_script(), min_size=0, max_size=5))
async def test_migration(
    alembic_config_factory: AlembicConfigFactory, scripts: list[models_old.Script]
) -> None:
    note(f'scripts: {scripts}')

    config = alembic_config_factory()
    url = config.get_main_option('sqlalchemy.url')
    note(f'url: {url}')

    # Enter data, in which multiple scripts can be current
    await to_thread(command.upgrade, config, REVISION_START)
    async with DB(url, model_base_class=models_old.Model, use_migration=False) as db:
        assert db.migration_revision == REVISION_START
        async with db.session.begin() as session:
            session.add_all(scripts)

    # Upgrade to the revision where at most one script is current. Make expected data.
    await to_thread(command.upgrade, config, REVISION_STAGE_ONE)
    async with DB(url, model_base_class=models_old.Model, use_migration=False) as db:
        assert db.migration_revision == REVISION_STAGE_ONE
        async with db.session() as session:
            loaded = await load_all(session, models_old.Model)
            expected = [repr(s) for s in loaded]

    # Upgrade to the target revision.
    await to_thread(command.upgrade, config, REVISION_NEW)

    # Downgrade and make actual data.
    await to_thread(command.downgrade, config, REVISION_START)
    async with DB(url, model_base_class=models_old.Model, use_migration=False) as db:
        assert db.migration_revision == REVISION_START
        async with db.session() as session:
            loaded = await load_all(session, models_old.Model)
            actual = [repr(s) for s in loaded]

    assert expected == actual
