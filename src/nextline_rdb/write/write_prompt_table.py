import asyncio

from nextline.events import OnEndPrompt, OnStartPrompt
from nextline.plugin.spec import hookimpl
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from nextline_rdb.db import DB
from nextline_rdb.models import Prompt, Run, Trace, TraceCall


class WritePromptTable:
    def __init__(self, db: DB) -> None:
        self._db = db

    @hookimpl
    async def on_start_prompt(self, event: OnStartPrompt) -> None:
        async with self._db.session.begin() as session:
            stmt = (
                select(TraceCall)
                .join(TraceCall.trace)
                .join(TraceCall.run)
                .filter(
                    Run.run_no == event.run_no,
                    Trace.trace_no == event.trace_no,
                    TraceCall.trace_call_no == event.trace_call_no,
                )
            )
            stmt = stmt.options(selectinload(TraceCall.trace).selectinload(Trace.run))
            while not (
                trace_call := (await session.execute(stmt)).scalar_one_or_none()
            ):
                await asyncio.sleep(0)
            prompt = Prompt(
                prompt_no=event.prompt_no,
                open=True,
                stdout=event.prompt_text,
                started_at=event.started_at,
                run=trace_call.trace.run,
                trace=trace_call.trace,
                trace_call=trace_call,
            )
            session.add(prompt)

    @hookimpl
    async def on_end_prompt(self, event: OnEndPrompt) -> None:
        async with self._db.session.begin() as session:
            stmt = (
                select(Prompt)
                .join(Run)
                .filter(Run.run_no == event.run_no, Prompt.prompt_no == event.prompt_no)
            )
            while not (prompt := (await session.execute(stmt)).scalar_one_or_none()):
                await asyncio.sleep(0)
            prompt.open = False
            prompt.command = event.command
            prompt.ended_at = event.ended_at
