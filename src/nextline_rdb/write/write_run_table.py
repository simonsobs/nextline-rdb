import asyncio
from datetime import timezone

from nextline.plugin.spec import Context, hookimpl
from sqlalchemy import select

from nextline_rdb.db import DB
from nextline_rdb.models import Run, Script


class WriteRunTable:
    def __init__(self, db: DB) -> None:
        self._db = db

    @hookimpl
    async def on_initialize_run(self, context: Context) -> None:
        assert (run_arg := context.run_arg)
        run_no = run_arg.run_no
        if isinstance(run_arg.statement, str):
            statement = run_arg.statement
        else:
            statement = None
        async with self._db.session.begin() as session:
            stmt = select(Script).filter_by(current=True)
            if statement is None:
                scripts = (await session.execute(stmt)).scalars().all()
                for script in scripts:
                    script.current = False
                run = Run(run_no=run_no, state='initialized')
                session.add(run)
            else:
                scripts = (await session.execute(stmt)).scalars().all()
                if len(scripts) > 1:
                    for script in scripts:
                        script.current = False
                    script = Script(script=statement, current=True)
                elif len(scripts) == 1:
                    if scripts[0].script != statement:
                        scripts[0].current = False
                        script = Script(script=statement, current=True)
                    else:
                        script = scripts[0]
                else:
                    script = Script(script=statement, current=True)
                run = Run(run_no=run_no, state='initialized', script=script)
                session.add(run)

    @hookimpl
    async def on_start_run(self, context: Context) -> None:
        assert (run_arg := context.run_arg)
        assert (running_process := context.running_process)
        started_at = running_process.process_created_at
        assert started_at.tzinfo is timezone.utc
        started_at = started_at.replace(tzinfo=None)
        run_no = run_arg.run_no
        async with self._db.session.begin() as session:
            stmt = select(Run).filter_by(run_no=run_no)
            while not (run := (await session.execute(stmt)).scalar_one_or_none()):
                await asyncio.sleep(0)
            run.state = 'running'
            run.started_at = started_at

    @hookimpl
    async def on_end_run(self, context: Context) -> None:
        assert (run_arg := context.run_arg)
        assert (exited_process := context.exited_process)
        assert (returned := exited_process.returned)
        ended_at = exited_process.process_exited_at
        assert ended_at.tzinfo is timezone.utc
        ended_at = ended_at.replace(tzinfo=None)
        run_no = run_arg.run_no
        async with self._db.session.begin() as session:
            stmt = select(Run).filter_by(run_no=run_no)
            while not (run := (await session.execute(stmt)).scalar_one_or_none()):
                await asyncio.sleep(0)
            run.state = 'finished'
            run.ended_at = ended_at
            run.exception = returned.fmt_exc
