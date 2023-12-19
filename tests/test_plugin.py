import asyncio

from async_asgi_testclient import TestClient
from nextlinegraphql.plugins.ctrl.test import run_statement
from nextlinegraphql.plugins.graphql.test import gql_request

from .schema.graphql import QUERY_HISTORY


async def test_one(client: TestClient):
    await run_statement(client)
    await asyncio.sleep(0.05)
    data = await gql_request(client, QUERY_HISTORY)
    runs = data['history']['runs']
    edges = runs['edges']
    assert 2 == len(edges)
    run = edges[1]['node']
    assert 2 == run['runNo']
    assert 'finished' == run['state']
    assert run['startedAt']
    assert run['endedAt']
    assert run['script']
    assert not run['exception']
