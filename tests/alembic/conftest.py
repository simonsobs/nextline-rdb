from pathlib import Path

import pytest
from alembic.config import Config

from nextline_rdb.db import ALEMBIC_INI


@pytest.fixture
def alembic_config() -> Config:
    assert Path(ALEMBIC_INI).is_file()
    config = Config(ALEMBIC_INI)
    return config


@pytest.fixture
def alembic_config_in_memory(alembic_config: Config) -> Config:
    config = alembic_config
    url = 'sqlite+aiosqlite://'
    config.set_main_option('sqlalchemy.url', url)
    return config


@pytest.fixture
def alembic_config_temp_sqlite(
    alembic_config: Config, tmp_path_factory: pytest.TempPathFactory
) -> Config:
    config = alembic_config
    dir = tmp_path_factory.mktemp('db')
    url = f'sqlite+aiosqlite:///{dir}/db.sqlite'
    config.set_main_option('sqlalchemy.url', url)
    return config
