import asyncio
from datetime import timezone
from logging import getLogger

from nextline.plugin.spec import Context, hookimpl
from nextline.spawned import RunArg
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from nextline_rdb.db import DB
from nextline_rdb.models import CurrentScript, Run, Script


class WriteRunTable:
    def __init__(self, db: DB) -> None:
        self._db = db
        self._logger = getLogger(__name__)

    @hookimpl
    async def on_start_run(self, context: Context) -> None:
        assert (run_arg := context.run_arg)
        assert (running_process := context.running_process)
        started_at = running_process.process_created_at
        assert started_at.tzinfo is timezone.utc
        started_at = started_at.replace(tzinfo=None)
        run_no = run_arg.run_no
        async with self._db.session.begin() as session:
            script = await self._find_script(run_arg, session)
            run = Run(
                run_no=run_no, state='running', started_at=started_at, script=script
            )
            session.add(run)

    async def _find_script(
        self, run_arg: RunArg, session: AsyncSession
    ) -> Script | None:
        statement = self._str_statement_or_none(run_arg)
        current_script = await self._load_current_script(session)
        match statement, current_script:
            case None, None:
                return None
            case None, CurrentScript() as cs:
                self._logger.warning(
                    'CurrentScript is not None, but run_arg.statement is None'
                )
                await session.delete(cs)
            case str(statement_), None:
                self._logger.warning(
                    'CurrentScript is None, but run_arg.statement is not None'
                )
                return Script(script=statement_, current=True)
            case str(statement_), CurrentScript() as cs:
                if not cs.script == statement:
                    self._logger.warning(
                        'The statement in CurrentScript is different from run_arg.statement'
                    )
                    s = Script(script=statement_)
                    cs.script = s
                return cs.script
        return None

    def _str_statement_or_none(self, run_arg: RunArg) -> str | None:
        if isinstance(run_arg.statement, str):
            return run_arg.statement
        return None

    async def _load_current_script(self, session: AsyncSession) -> CurrentScript | None:
        stmt = select(CurrentScript).options(selectinload(CurrentScript.script))
        return (await session.execute(stmt)).scalar_one_or_none()

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
