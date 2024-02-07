from nextline.plugin.spec import Context, hookimpl
from nextline.spawned import RunArg
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from nextline_rdb.db import DB
from nextline_rdb.models import CurrentScript, Script


class WriteScriptTable:
    def __init__(self, db: DB) -> None:
        self._db = db

    @hookimpl
    async def on_initialize_run(self, context: Context) -> None:
        assert (run_arg := context.run_arg)
        statement = self._str_statement_or_none(run_arg)
        if statement is not None:
            await self._on_initialize_run_with_statement(statement)
        else:
            await self._on_initialize_run_without_statement()

    def _str_statement_or_none(self, run_arg: RunArg) -> str | None:
        if isinstance(run_arg.statement, str):
            return run_arg.statement
        return None

    async def _on_initialize_run_without_statement(self) -> None:
        async with self._db.session.begin() as session:
            current_script = await self._load_current_script(session)
            if current_script is not None:
                await session.delete(current_script)

    async def _on_initialize_run_with_statement(self, statement: str) -> None:
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

    async def _load_current_script(self, session: AsyncSession) -> CurrentScript | None:
        stmt = select(CurrentScript).options(selectinload(CurrentScript.script))
        return (await session.execute(stmt)).scalar_one_or_none()
