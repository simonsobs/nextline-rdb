from pathlib import Path

import pytest
from alembic.config import Config

from nextline_rdb.db import ALEMBIC_INI


@pytest.fixture
def alembic_config() -> Config:
    assert Path(ALEMBIC_INI).is_file()
    config = Config(ALEMBIC_INI)
    return config
