from sqlalchemy import select
from sqlalchemy.orm import selectinload

from nextline.events import OnEndTraceCall, OnStartTraceCall
from nextline.plugin.spec import hookimpl
from nextline.types import TraceNo
from nextline_rdb.db import DB
from nextline_rdb.models import Run, Trace, TraceCall
from nextline_rdb.utils import until_scalar_one


class WriteTraceCallTable:
    def __init__(self, db: DB) -> None:
        self._db = db
        self._running_trace_nos = set[TraceNo]()

    @hookimpl
    async def on_start_trace_call(self, event: OnStartTraceCall) -> None:
        async with self._db.session.begin() as session:
            stmt = (
                select(Trace)
                .join(Run)
                .filter(Run.run_no == event.run_no, Trace.trace_no == event.trace_no)
            )
            stmt = stmt.options(selectinload(Trace.run))
            trace = await until_scalar_one(session, stmt)
            trace_call = TraceCall(
                trace_call_no=event.trace_call_no,
                started_at=event.started_at,
                file_name=event.file_name,
                line_no=event.line_no,
                event=event.event,
                run=trace.run,
                trace=trace,
            )
            session.add(trace_call)

    @hookimpl
    async def on_end_trace_call(self, event: OnEndTraceCall) -> None:
        async with self._db.session.begin() as session:
            stmt = (
                select(TraceCall)
                .join(Trace)
                .join(Run)
                .filter(
                    Run.run_no == event.run_no,
                    Trace.trace_no == event.trace_no,
                    TraceCall.trace_call_no == event.trace_call_no,
                )
            )
            trace_call = await until_scalar_one(session, stmt)
            trace_call.ended_at = event.ended_at
