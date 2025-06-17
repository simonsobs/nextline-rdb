import base64
import datetime as dt
from typing import TypedDict

from nextline_rdb.models import Run


def Cursor(i: int) -> str:
    return base64.b64encode(f'{i}'.encode()).decode()


class Filter(TypedDict, total=False):
    startedAfter: str | None
    startedBefore: str | None
    endedAfter: str | None
    endedBefore: str | None


class Variables(TypedDict, total=False):
    before: str | None
    after: str | None
    first: int | None
    last: int | None
    filter: Filter | None


class PageInfo(TypedDict):
    hasPreviousPage: bool
    hasNextPage: bool
    startCursor: str | None
    endCursor: str | None


class Node(TypedDict):
    id: int
    runNo: int
    startedAt: str | None
    endedAt: str | None


class Edge(TypedDict):
    cursor: str
    node: Node


def dt_to_iso(dt_: dt.datetime | None) -> str | None:
    return dt_.isoformat() if dt_ else None


def to_node(run: Run) -> Node:
    return Node(
        id=run.id,
        runNo=run.run_no,
        startedAt=dt_to_iso(run.started_at),
        endedAt=dt_to_iso(run.ended_at),
    )
