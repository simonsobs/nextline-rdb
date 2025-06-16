import base64
from typing import TypedDict


def Cursor(i: int) -> str:
    return base64.b64encode(f'{i}'.encode()).decode()


class Variables(TypedDict, total=False):
    before: str | None
    after: str | None
    first: int | None
    last: int | None


class PageInfo(TypedDict):
    hasPreviousPage: bool
    hasNextPage: bool
    startCursor: str | None
    endCursor: str | None


class Node(TypedDict):
    id: int
    runNo: int


class Edge(TypedDict):
    cursor: str
    node: Node
