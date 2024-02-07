import asyncio
from collections.abc import AsyncIterator, Callable
from pathlib import Path
from typing import Optional

import pytest
from nextline import Nextline
from nextline.events import OnStartPrompt
from nextline.plugin.spec import Context, hookimpl
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from nextline_rdb import DB
from nextline_rdb import models as db_models
from nextline_rdb import write


async def test_one(adb: DB, run_nextline, statement):
    del run_nextline

    async with adb.session() as session:
        stmt = select(db_models.Run).options(selectinload(db_models.Run.script))
        runs = (await session.scalars(stmt)).all()
        assert 1 == len(runs)
        run = runs[0]
        assert 2 == run.run_no
        assert run.started_at
        assert run.ended_at
        assert run.script
        assert statement == run.script.script
        assert not run.exception

        traces = (await session.scalars(select(db_models.Trace))).all()
        assert 5 == len(traces)
        run_no = 2
        trace_no = 0
        for trace in traces:
            trace_no += 1
            assert trace_no == trace.trace_no
            assert run_no == trace.run_no
            assert trace.started_at
            assert trace.ended_at

        prompts = (await session.scalars(select(db_models.Prompt))).all()
        assert 58 == len(prompts)
        for prompt in prompts:
            assert run_no == prompt.run_no
            assert prompt.trace_no
            assert prompt.started_at
            assert prompt.line_no
            assert prompt.file_name
            assert prompt.event

        stdouts = (await session.scalars(select(db_models.Stdout))).all()
        assert 1 == len(stdouts)
        # for stdout in stdouts:
        #     assert run_no == stdout.run_no
        #     assert stdout.text
        #     assert stdout.written_at


@pytest.fixture
def monkey_patch_syspath(monkeypatch: pytest.MonkeyPatch) -> None:
    here = Path(__file__).resolve().parent
    path = here / 'example_script'
    monkeypatch.syspath_prepend(str(path))
    return


@pytest.fixture
def statement(monkey_patch_syspath: None) -> str:
    del monkey_patch_syspath
    here = Path(__file__).resolve().parent
    path = here / 'example_script'
    return (path / 'script.py').read_text()


@pytest.fixture
async def run_nextline(adb: DB, statement: str) -> None:
    nextline = Nextline(statement, trace_threads=True, trace_modules=True)
    write.register(nextline=nextline, db=adb)
    nextline.register(Control())
    async with nextline:
        await run_statement(nextline, statement)


@pytest.fixture
async def adb(url: str) -> AsyncIterator[DB]:
    async with DB(url=url) as adb:
        yield adb


@pytest.fixture
def url(tmp_url_factory: Callable[[], str]) -> str:
    return tmp_url_factory()


@pytest.fixture(scope='session')
def tmp_url_factory(tmp_path_factory: pytest.TempPathFactory) -> Callable[[], str]:
    def factory() -> str:
        dir = tmp_path_factory.mktemp('db')
        url = f'sqlite:///{dir}/db.sqlite'
        return url

    return factory


async def run_statement(nextline: Nextline, statement: Optional[str] = None) -> None:
    await asyncio.sleep(0.01)
    await nextline.reset(statement=statement)
    await asyncio.sleep(0.01)
    async with nextline.run_session():
        pass
    await asyncio.sleep(0.01)


class Control:
    @hookimpl
    async def on_start_prompt(self, context: Context, event: OnStartPrompt) -> None:
        nextline = context.nextline
        if event.event == 'line':
            line = nextline.get_source_line(
                line_no=event.line_no, file_name=event.file_name
            )
            command = find_command(line) or 'next'
        else:
            command = 'next'
        await asyncio.sleep(0.01)
        await nextline.send_pdb_command(command, event.prompt_no, event.trace_no)


def find_command(line: str) -> Optional[str]:
    '''The Pdb command indicated in a comment

    For example, returns 'step' for the line 'func()  # step'
    '''
    import re

    if not (comment := extract_comment(line)):
        return None
    regex = re.compile(r'^# +(\w+) *$')
    match = regex.search(comment)
    if match:
        return match.group(1)
    return None


def extract_comment(line: str) -> Optional[str]:
    import io
    import tokenize

    comments = [
        val
        for type, val, *_ in tokenize.generate_tokens(io.StringIO(line).readline)
        if type == tokenize.COMMENT
    ]
    if comments:
        return comments[0]
    return None
