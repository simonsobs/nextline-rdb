from collections.abc import Callable
from pathlib import Path

import pytest
import tomli
import tomli_w
from async_asgi_testclient import TestClient
from nextlinegraphql import create_app
from nextlinegraphql.plugins.ctrl.graphql import MUTATE_RUN_AND_CONTINUE
from nextlinegraphql.plugins.graphql.test import gql_request

from nextline_rdb.db import DB
from nextline_rdb.models.strategies import st_model_run_list

from .schema.graphql import QUERY_RDB_CONNECTIONS


async def test_plugin(set_new_url: Callable[[], str]):
    # Enter some runs into the database.
    runs = st_model_run_list(generate_traces=False, max_size=2).example()

    url = set_new_url()
    async with DB(url) as db:
        async with db.session.begin() as session:
            session.add_all(runs)

    #
    expected_n_runs = len(runs) + 1  # +1 for the new run

    # Execute GraphQL queries.
    app = create_app()  # the plugin is loaded here
    async with TestClient(app) as client:
        data = await gql_request(client, MUTATE_RUN_AND_CONTINUE)
        assert data['runAndContinue']
        data = await gql_request(client, QUERY_RDB_CONNECTIONS)
        n_runs = len(data['rdb']['runs']['edges'])

    assert n_runs == expected_n_runs


def test_fixture(settings_path: Path, set_new_url: Callable[[], str]):
    from nextline_rdb import plugin

    assert str(settings_path) in plugin.SETTINGS

    settings = tomli.loads(settings_path.read_text())
    url_org = settings['db']['url']

    url = set_new_url()
    assert url != url_org

    settings = tomli.loads(settings_path.read_text())
    assert url == settings['db']['url']


@pytest.fixture(scope='module')
def set_new_url(
    settings_path: Path, tmp_url_factory: Callable[[], str]
) -> Callable[[], str]:
    def _f() -> str:
        url = tmp_url_factory()
        settings = tomli.loads(settings_path.read_text())
        settings['db']['url'] = url
        settings_path.write_text(tomli_w.dumps(settings))
        return url

    return _f


@pytest.fixture(autouse=True)
def monkeypatch_settings_path(monkeypatch: pytest.MonkeyPatch, settings_path: Path):
    from nextline_rdb import plugin

    monkeypatch.setattr(plugin, 'SETTINGS', (str(settings_path),))


@pytest.fixture(scope='module')
def settings_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    dir = tmp_path_factory.mktemp('config')
    settings_path = dir / 'settings.toml'
    url = 'sqlite+aiosqlite://'
    data = {'db': {'url': url}}
    toml_str = tomli_w.dumps(data)
    with settings_path.open('w') as f:
        f.write(toml_str)
    return settings_path


@pytest.fixture(scope='module')
def tmp_url_factory(tmp_path_factory: pytest.TempPathFactory) -> Callable[[], str]:
    def factory() -> str:
        dir = tmp_path_factory.mktemp('db')
        url = f'sqlite+aiosqlite:///{dir}/db.sqlite'
        return url

    return factory
