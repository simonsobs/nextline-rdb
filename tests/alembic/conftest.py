from pathlib import Path

import pytest


@pytest.fixture
def in_alembic_dir(monkeypatch: pytest.MonkeyPatch):
    import nextline_rdb

    path = Path(nextline_rdb.__file__).parent

    monkeypatch.chdir(path)
