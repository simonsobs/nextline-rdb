from pathlib import Path

import pytest

from nextline_rdb.db import ALEMBIC_INI


@pytest.fixture
def in_alembic_dir(monkeypatch: pytest.MonkeyPatch) -> Path:
    '''Move to the directory with alembic.ini'''
    path = Path(ALEMBIC_INI).parent
    monkeypatch.chdir(path)
    return path
