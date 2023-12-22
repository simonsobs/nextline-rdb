from collections.abc import Callable
from pathlib import Path

import pytest
import tomli
import tomli_w
from async_asgi_testclient import TestClient
from nextlinegraphql import create_app
from nextlinegraphql.plugins.ctrl.graphql import MUTATE_RUN_AND_CONTINUE
from nextlinegraphql.plugins.graphql.test import gql_request

from nextline_rdb.db import AsyncDB
from nextline_rdb.models.strategies import st_model_run_list
from nextline_rdb.utils.strategies import st_python_scripts

from .schema.graphql import QUERY_HISTORY


@pytest.mark.parametrize('n_runs', [0, 1, 3])
@pytest.mark.parametrize('last_script_none', [True, False])
async def test_plugin(
    set_new_url: Callable[[], str], n_runs: int, last_script_none: bool
):
    # NOTE: Use Pytest's parametrize instead of Hypothesis's given in order to
    #       limit the number of examples.

    if not n_runs and not last_script_none:
        return

    # Enter some runs into the database.
    runs = st_model_run_list(
        generate_traces=False, min_size=n_runs, max_size=n_runs
    ).example()

    assert n_runs == len(runs)
    last_run = runs[-1] if runs else None
    if last_run:
        if last_script_none:
            last_run.script = None
        else:
            last_run.script = st_python_scripts().example()

    url = set_new_url()
    async with AsyncDB(url) as db:
        async with db.session.begin() as session:
            session.add_all(runs)

    #
    expected_new_run_no = last_run.run_no + 1 if last_run else None
    expected_new_run_script = last_run.script if last_run else None

    # Execute GraphQL queries.
    app = create_app()  # the plugin is loaded here
    async with TestClient(app) as client:
        data = await gql_request(client, MUTATE_RUN_AND_CONTINUE)
        assert data['runAndContinue']
        data = await gql_request(client, QUERY_HISTORY)
        new_run = data['history']['runs']['edges'][-1]['node']

    # Assert the results.
    if expected_new_run_no:
        assert expected_new_run_no == new_run['runNo']
    if expected_new_run_script:
        assert expected_new_run_script == new_run['script']


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
