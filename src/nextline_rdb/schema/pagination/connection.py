'''Pagination based on the example code in strawberry doc

Strawberry doc: https://strawberry.rocks/docs/guides/pagination/connections
Relay doc: https://relay.dev/graphql/connections.htm
'''

from collections.abc import Callable, Coroutine
from typing import Any, Generic, Optional, TypeVar

import strawberry

_T = TypeVar('_T')


@strawberry.type
class Edge(Generic[_T]):
    node: _T
    cursor: str


@strawberry.type
class PageInfo:
    has_next_page: bool
    has_previous_page: bool
    start_cursor: Optional[str] = None
    end_cursor: Optional[str] = None


@strawberry.type
class Connection(Generic[_T]):
    page_info: PageInfo
    total_count: int
    edges: list[Edge[_T]]


async def query_connection(
    query_edges: Callable[..., Coroutine[Any, Any, list[Edge[_T]]]],
    query_total_count: Callable[..., Coroutine[Any, Any, int]],
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> Connection[_T]:
    forward = after or (first is not None)
    backward = before or (last is not None)

    if forward and backward:
        raise ValueError('Only either after/first or before/last is allowed')

    if forward:
        if first is not None:
            first += 1  # add one for has_next_page
        edges = await query_edges(after=after, first=first)
        has_previous_page = not not after
        if has_next_page := len(edges) == first:
            edges = edges[:-1]
    elif backward:
        if last is not None:
            last += 1  # add one for has_previous_page
        edges = await query_edges(before=before, last=last)
        if has_previous_page := len(edges) == last:
            edges = edges[1:]
        has_next_page = not not before
    else:
        edges = await query_edges()
        has_previous_page = False
        has_next_page = False

    total_count = await query_total_count()

    page_info = PageInfo(
        has_previous_page=has_previous_page,
        has_next_page=has_next_page,
        start_cursor=edges[0].cursor if edges else None,
        end_cursor=edges[-1].cursor if edges else None,
    )

    return Connection(page_info=page_info, total_count=total_count, edges=edges)
