import asyncio

from nextline.events import OnWriteStdout
from nextline.plugin.spec import hookimpl
from sqlalchemy import select

from nextline_rdb.db import DB
from nextline_rdb.models import Run, Stdout, Trace


class WriteStdoutTable:
    def __init__(self, db: DB) -> None:
        self._db = db

    @hookimpl
    async def on_write_stdout(self, event: OnWriteStdout) -> None:
        async with self._db.session.begin() as session:
            select_runs = select(Run).filter_by(run_no=event.run_no)
            while not (
                run := (await session.execute(select_runs)).scalar_one_or_none()
            ):
                await asyncio.sleep(0)
            select_traces = select(Trace).filter_by(
                run_no=event.run_no, trace_no=event.trace_no
            )
            while not (
                trace := (await session.execute(select_traces)).scalar_one_or_none()
            ):
                await asyncio.sleep(0)
            stdout = Stdout(
                run_no=event.run_no,
                trace_no=event.trace_no,
                text=event.text,
                written_at=event.written_at,
                run=run,
                trace=trace,
            )
            session.add(stdout)
