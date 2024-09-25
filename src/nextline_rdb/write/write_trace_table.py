from datetime import timezone

from sqlalchemy import select

from nextline.events import OnEndRun, OnEndTrace, OnStartTrace
from nextline.plugin.spec import hookimpl
from nextline.types import TraceNo
from nextline_rdb.db import DB
from nextline_rdb.models import Run, Trace
from nextline_rdb.utils import until_scalar_one


class WriteTraceTable:
    def __init__(self, db: DB) -> None:
        self._db = db
        self._running_trace_nos = set[TraceNo]()

    @hookimpl
    async def on_start_trace(self, event: OnStartTrace) -> None:
        async with self._db.session.begin() as session:
            stmt = select(Run).filter_by(run_no=event.run_no)
            run = await until_scalar_one(session, stmt)
            trace = Trace(
                trace_no=event.trace_no,
                state='running',
                thread_no=event.thread_no,
                task_no=event.task_no,
                started_at=event.started_at,
                run=run,
            )
            session.add(trace)
        self._running_trace_nos.add(event.trace_no)

    @hookimpl
    async def on_end_trace(self, event: OnEndTrace) -> None:
        async with self._db.session.begin() as session:
            stmt = (
                select(Trace)
                .join(Run)
                .filter(Run.run_no == event.run_no, Trace.trace_no == event.trace_no)
            )
            trace = await until_scalar_one(session, stmt)
            trace.state = 'finished'
            trace.ended_at = event.ended_at
        self._running_trace_nos.remove(event.trace_no)

    @hookimpl
    async def on_start_run(self) -> None:
        self._running_trace_nos.clear()

    @hookimpl
    async def on_end_run(self, event: OnEndRun) -> None:
        assert event.ended_at.tzinfo is timezone.utc
        ended_at = event.ended_at.replace(tzinfo=None)
        run_no = event.run_no
        async with self._db.session.begin() as session:
            stmt = (
                select(Trace)
                .join(Run)
                .filter(
                    Run.run_no == run_no, Trace.trace_no.in_(self._running_trace_nos)
                )
            )
            traces = (await session.execute(stmt)).scalars().all()
            for trace in traces:
                trace.state = 'finished'
                trace.ended_at = ended_at
        self._running_trace_nos.clear()
