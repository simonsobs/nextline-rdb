from asyncio import to_thread

from alembic import command
from hypothesis import given, note
from sqlalchemy import select

from nextline_rdb.alembic.models import rev_5a08750d6760 as models_old
from nextline_rdb.alembic.models import rev_f9a742bb2297 as models_new
from nextline_rdb.alembic.models.rev_5a08750d6760.strategies import st_model_run_list
from nextline_rdb.db import DB

from .conftest import AlembicConfigFactory

REVISION_OLD = '5a08750d6760'
REVISION_NEW = 'f9a742bb2297'


@given(runs=st_model_run_list(generate_traces=True))
async def test_migration(
    alembic_config_factory: AlembicConfigFactory, runs: list[models_old.Run]
) -> None:
    note(f'runs: {runs}')

    config = alembic_config_factory()
    url = config.get_main_option('sqlalchemy.url')
    note(f'url: {url}')

    await to_thread(command.upgrade, config, REVISION_OLD)
    async with DB(url, model_base_class=models_old.Model, use_migration=False) as db:
        assert db.migration_revision == REVISION_OLD
        async with db.session.begin() as session:
            session.add_all(runs)

    await to_thread(command.upgrade, config, REVISION_NEW)
    async with DB(url, model_base_class=models_new.Model, use_migration=False) as db:
        assert db.migration_revision == REVISION_NEW

    await to_thread(command.downgrade, config, REVISION_OLD)
    async with DB(url, model_base_class=models_old.Model, use_migration=False) as db:
        assert db.migration_revision == REVISION_OLD
        async with db.session() as session:
            select_run = select(models_old.Run).order_by(models_old.Run.run_no)
            runs_ = (await session.scalars(select_run)).all()

    assert repr(runs) == repr(runs_)
