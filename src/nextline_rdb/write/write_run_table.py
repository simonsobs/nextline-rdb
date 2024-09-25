from datetime import timezone
from logging import getLogger

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from nextline.events import OnEndRun, OnStartRun
from nextline.plugin.spec import hookimpl
from nextline_rdb.db import DB
from nextline_rdb.models import CurrentScript, Run, Script
from nextline_rdb.utils import until_scalar_one


class WriteRunTable:
    def __init__(self, db: DB) -> None:
        self._db = db
        self._logger = getLogger(__name__)

    @hookimpl
    async def on_start_run(self, event: OnStartRun) -> None:
        assert event.started_at.tzinfo is timezone.utc
        started_at = event.started_at.replace(tzinfo=None)
        async with self._db.session.begin() as session:
            script = await self._find_script(event, session)
            run = Run(
                run_no=event.run_no,
                state='running',
                started_at=started_at,
                script=script,
            )
            session.add(run)

    async def _find_script(
        self, event: OnStartRun, session: AsyncSession
    ) -> Script | None:
        statement = self._str_statement_or_none(event)
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
                if not cs.script.script == statement:
                    self._logger.warning(
                        'The statement in CurrentScript is different from run_arg.statement'
                    )
                    s = Script(script=statement_)
                    cs.script = s
                return cs.script
        return None

    def _str_statement_or_none(self, event: OnStartRun) -> str | None:
        if isinstance(event.statement, str):
            return event.statement
        return None

    async def _load_current_script(self, session: AsyncSession) -> CurrentScript | None:
        stmt = select(CurrentScript).options(selectinload(CurrentScript.script))
        return (await session.execute(stmt)).scalar_one_or_none()

    @hookimpl
    async def on_end_run(self, event: OnEndRun) -> None:
        assert event.ended_at.tzinfo is timezone.utc
        ended_at = event.ended_at.replace(tzinfo=None)
        async with self._db.session.begin() as session:
            stmt = select(Run).filter_by(run_no=event.run_no)
            run = await until_scalar_one(session, stmt)
            run.state = 'finished'
            run.ended_at = ended_at
            run.exception = event.raised
