import asyncio

from nextline.events import OnEndPrompt, OnStartPrompt
from nextline.plugin.spec import hookimpl
from sqlalchemy import select

from nextline_rdb.db import DB
from nextline_rdb.models import Prompt, Run, Trace


class WritePromptTable:
    def __init__(self, db: DB) -> None:
        self._db = db

    @hookimpl
    async def on_start_prompt(self, event: OnStartPrompt) -> None:
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
            prompt = Prompt(
                run_no=event.run_no,
                trace_no=event.trace_no,
                prompt_no=event.prompt_no,
                open=True,
                event=event.event,
                file_name=event.file_name,
                line_no=event.line_no,
                stdout=event.prompt_text,
                started_at=event.started_at,
                run=run,
                trace=trace,
            )
            session.add(prompt)

    @hookimpl
    async def on_end_prompt(self, event: OnEndPrompt) -> None:
        async with self._db.session.begin() as session:
            stmt = select(Prompt).filter_by(
                run_no=event.run_no, prompt_no=event.prompt_no
            )
            while not (prompt := (await session.execute(stmt)).scalar_one_or_none()):
                await asyncio.sleep(0)
            prompt.open = False
            prompt.command = event.command
            prompt.ended_at = event.ended_at
