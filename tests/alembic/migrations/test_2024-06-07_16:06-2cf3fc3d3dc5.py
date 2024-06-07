from asyncio import to_thread

from alembic import command
from hypothesis import Phase, given, note, settings

from nextline_rdb.alembic.models import rev_4dc6a93dfed8 as models_old
from nextline_rdb.alembic.models.rev_4dc6a93dfed8.strategies import (
    st_model_instance_list,
)
from nextline_rdb.db import DB
from nextline_rdb.utils import load_all

from .conftest import AlembicConfigFactory

REVISION_START = '4dc6a93dfed8'
REVISION_NEW = '2cf3fc3d3dc5'


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(instances=st_model_instance_list(min_size=0, max_size=5))
async def test_migration(
    alembic_config_factory: AlembicConfigFactory, instances: list[models_old.Model]
) -> None:
    note(f'scripts: {instances}')

    config = alembic_config_factory()
    url = config.get_main_option('sqlalchemy.url')
    note(f'url: {url}')

    # Enter data
    await to_thread(command.upgrade, config, REVISION_START)
    async with DB(url, model_base_class=models_old.Model, use_migration=False) as db:
        assert db.migration_revision == REVISION_START
        async with db.session.begin() as session:
            session.add_all(instances)

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
