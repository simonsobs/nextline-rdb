from collections.abc import Callable

import pytest
import strawberry
from async_asgi_testclient import TestClient
from hypothesis import given, settings
from hypothesis import strategies as st
from nextlinegraphql.plugins.ctrl.test import run_statement
from nextlinegraphql.plugins.graphql.test import gql_request

from nextline_rdb.db import DB
from nextline_rdb.db.adb import AsyncDB
from nextline_rdb.models.strategies import st_model_run_list
from nextline_rdb.schema import Query
from nextline_rdb.utils import ensure_sync_url

from ..graphql import QUERY_HISTORY


async def test_one(client: TestClient):
    await run_statement(client)

    data = await gql_request(client, QUERY_HISTORY)
    # print(data["history"])
    runs = data["history"]["runs"]
    edges = runs["edges"]
    # assert 2 == len(runs)
    run = edges[1]["node"]
    assert 2 == run["runNo"]
    assert "finished" == run["state"]
    assert run["startedAt"]
    assert run["endedAt"]
    assert run["script"]
    assert not run["exception"]


@given(st.data())
@settings(max_examples=200)
async def test_st_model_run_lists(
    tmp_url_factory: Callable[[], str],
    data: st.DataObject,
) -> None:
    max_size = 10
    runs = data.draw(st_model_run_list(generate_traces=True, max_size=max_size))

    # ic(runs)

    schema = strawberry.Schema(query=Query)

    url = tmp_url_factory()

    # db_ = DB(ensure_sync_url(url))
    with DB(ensure_sync_url(url)) as db_:
        with db_.session() as session:
            pass

    async with AsyncDB(url, use_migration=False) as db:
        async with db.session.begin() as session:
            session.add_all(runs)

    # db_ = DB(ensure_sync_url(url))
    with DB(ensure_sync_url(url)) as db_:
        # with db_.session() as session:
        #     pass
        # resp = schema.execute_sync(QUERY_HISTORY, context_value={'db': db_})
        resp = await schema.execute(QUERY_HISTORY, context_value={'db': db_})
        # ic(resp)
        assert not resp.errors


@pytest.fixture(scope='session')
def tmp_url_factory(tmp_path_factory: pytest.TempPathFactory) -> Callable[[], str]:
    def factory() -> str:
        dir = tmp_path_factory.mktemp('db')
        url = f'sqlite+aiosqlite:///{dir}/db.sqlite'
        return url

    return factory
