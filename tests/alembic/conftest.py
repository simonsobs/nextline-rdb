from pathlib import Path

import pytest

import nextline_rdb


@pytest.fixture
def in_alembic_dir(monkeypatch: pytest.MonkeyPatch) -> Path:
    '''Move to the directory with alembic.ini'''
    path = Path(nextline_rdb.__file__).parent
    assert (path / 'alembic.ini').is_file()
    monkeypatch.chdir(path)
    return path
