from typing import Callable

import pytest
from alembic.config import Config

from nextline_rdb.db import ALEMBIC_INI

AlembicConfigFactory = Callable[[], Config]


@pytest.fixture(scope='session')
def alembic_config_factory(
    tmp_path_factory: pytest.TempPathFactory,
) -> Callable[[], Config]:
    def factory() -> Config:
        config = Config(ALEMBIC_INI)
        dir = tmp_path_factory.mktemp('db')
        url = f'sqlite+aiosqlite:///{dir}/db.sqlite'
        config.set_main_option('sqlalchemy.url', url)
        return config

    return factory
