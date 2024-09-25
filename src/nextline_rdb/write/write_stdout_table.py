from sqlalchemy import select

from nextline.events import OnWriteStdout
from nextline.plugin.spec import hookimpl
from nextline_rdb.db import DB
from nextline_rdb.models import Run, Stdout, Trace
from nextline_rdb.utils import until_scalar_one


class WriteStdoutTable:
    def __init__(self, db: DB) -> None:
        self._db = db

    @hookimpl
    async def on_write_stdout(self, event: OnWriteStdout) -> None:
        async with self._db.session.begin() as session:
            select_runs = select(Run).filter_by(run_no=event.run_no)
            run = await until_scalar_one(session, select_runs)
            select_traces = (
                select(Trace)
                .join(Run)
                .filter(Run.run_no == event.run_no, Trace.trace_no == event.trace_no)
            )
            trace = await until_scalar_one(session, select_traces)
            stdout = Stdout(
                text=event.text,
                written_at=event.written_at,
                run=run,
                trace=trace,
            )
            session.add(stdout)
