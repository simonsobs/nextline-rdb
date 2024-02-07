import asyncio
from datetime import timezone

from nextline.plugin.spec import Context, hookimpl
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from nextline_rdb.db import DB
from nextline_rdb.models import CurrentScript, Run, Script


class WriteRunTable:
    def __init__(self, db: DB) -> None:
        self._db = db

    @hookimpl
    async def on_initialize_run(self, context: Context) -> None:
        assert (run_arg := context.run_arg)
        run_no = run_arg.run_no
        if isinstance(run_arg.statement, str):
            statement = run_arg.statement
            await self._on_initialize_run_with_statement(run_no, statement)
        else:
            await self._on_initialize_run_without_statement(run_no)

    async def _on_initialize_run_without_statement(self, run_no: int) -> None:
        async with self._db.session.begin() as session:
            current_script = await self._load_current_script(session)
            if current_script is not None:
                await session.delete(current_script)
            run = Run(run_no=run_no, state='initialized')
            session.add(run)

    async def _on_initialize_run_with_statement(
        self, run_no: int, statement: str
    ) -> None:
        async with self._db.session.begin() as session:
            current_script = await self._load_current_script(session)
            if current_script is not None:
                if current_script.script.script == statement:
                    script = current_script.script
                else:
                    script = Script(script=statement)
                    current_script.script = script
            else:
                script = Script(script=statement)
                current_script = CurrentScript(script=script)
                session.add(current_script)
            run = Run(run_no=run_no, state='initialized', script=script)
            session.add(run)

    async def _load_current_script(self, session: AsyncSession) -> CurrentScript | None:
        stmt = select(CurrentScript).options(selectinload(CurrentScript.script))
        return (await session.execute(stmt)).scalar_one_or_none()

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
