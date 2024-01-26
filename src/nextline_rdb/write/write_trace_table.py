import asyncio
from datetime import timezone

from nextline.events import OnEndTrace, OnStartTrace
from nextline.plugin.spec import Context, hookimpl
from nextline.types import TraceNo
from sqlalchemy import select

from nextline_rdb.db import DB
from nextline_rdb.models import Run, Trace


class WriteTraceTable:
    def __init__(self, db: DB) -> None:
        self._db = db
        self._running_trace_nos = set[TraceNo]()

    @hookimpl
    async def on_start_trace(self, event: OnStartTrace) -> None:
        async with self._db.session.begin() as session:
            stmt = select(Run).filter_by(run_no=event.run_no)
            while not (run := (await session.execute(stmt)).scalar_one_or_none()):
                await asyncio.sleep(0)
            trace = Trace(
                run_no=event.run_no,
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
            stmt = select(Trace).filter_by(run_no=event.run_no, trace_no=event.trace_no)
            while not (trace := (await session.execute(stmt)).scalar_one_or_none()):
                await asyncio.sleep(0)
            trace.state = 'finished'
            trace.ended_at = event.ended_at
        self._running_trace_nos.remove(event.trace_no)

    @hookimpl
    async def on_start_run(self) -> None:
        self._running_trace_nos.clear()

    @hookimpl
    async def on_end_run(self, context: Context) -> None:
        assert (run_arg := context.run_arg)
        assert (exited_process := context.exited_process)
        ended_at = exited_process.process_exited_at
        assert ended_at.tzinfo is timezone.utc
        ended_at = ended_at.replace(tzinfo=None)
        run_no = run_arg.run_no
        async with self._db.session.begin() as session:
            stmt = (
                select(Trace)
                .filter_by(run_no=run_no)
                .filter(Trace.trace_no.in_(self._running_trace_nos))
            )
            traces = (await session.execute(stmt)).scalars().all()
            for trace in traces:
                trace.state = 'finished'
                trace.ended_at = ended_at
        self._running_trace_nos.clear()
