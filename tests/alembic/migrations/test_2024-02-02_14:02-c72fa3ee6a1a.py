from asyncio import to_thread

from alembic import command
from hypothesis import given, note
from hypothesis import strategies as st
from sqlalchemy import select

from nextline_rdb.alembic.models import rev_f9a742bb2297 as models_old
from nextline_rdb.alembic.models.rev_f9a742bb2297.strategies import st_model_script
from nextline_rdb.db import DB

from .conftest import AlembicConfigFactory

REVISION_OLD = 'f9a742bb2297'
REVISION_NEW = 'c72fa3ee6a1a'


@given(scripts=st.lists(st_model_script(), min_size=0, max_size=5))
async def test_migration(
    alembic_config_factory: AlembicConfigFactory, scripts: list[models_old.Script]
) -> None:
    note(f'scripts: {scripts}')

    config = alembic_config_factory()
    url = config.get_main_option('sqlalchemy.url')
    note(f'url: {url}')

    await to_thread(command.upgrade, config, REVISION_OLD)
    async with DB(url, model_base_class=models_old.Model, use_migration=False) as db:
        assert db.migration_revision == REVISION_OLD
        async with db.session.begin() as session:
            session.add_all(scripts)

    await to_thread(command.upgrade, config, REVISION_NEW)

    await to_thread(command.downgrade, config, REVISION_OLD)
    async with DB(url, model_base_class=models_old.Model, use_migration=False) as db:
        assert db.migration_revision == REVISION_OLD
        async with db.session() as session:
            select_scripts = select(models_old.Script).order_by(models_old.Script.id)
            scripts_ = (await session.execute(select_scripts)).scalars().all()
            currents = [s for s in scripts_ if s.current]
            assert len(currents) in (0, 1)
