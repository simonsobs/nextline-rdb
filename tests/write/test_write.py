import asyncio
from collections.abc import Iterator
from pathlib import Path
from typing import Optional, cast

import pytest
from nextline import Nextline
from nextline.types import PromptInfo
from nextline.utils import merge_aiters
from sqlalchemy.orm import Session

from nextline_rdb import DB
from nextline_rdb import models as db_models
from nextline_rdb import write_db


def test_one(db: DB, run_nextline, statement):
    del run_nextline
    with db.session() as session:
        session = cast(Session, session)
        runs = session.query(db_models.Run).all()  # type: ignore
        assert 2 == len(runs)
        run = runs[1]
        assert 2 == run.run_no
        assert run.started_at
        assert run.ended_at
        assert statement == run.script
        assert not run.exception

        traces = session.query(db_models.Trace).all()  # type: ignore
        assert 5 == len(traces)
        run_no = 2
        trace_no = 0
        for trace in traces:
            trace_no += 1
            assert trace_no == trace.trace_no
            assert run_no == trace.run_no
            assert trace.started_at
            assert trace.ended_at

        prompts = session.query(db_models.Prompt).all()  # type: ignore
        assert 58 == len(prompts)
        for prompt in prompts:
            assert run_no == prompt.run_no
            assert prompt.trace_no
            assert prompt.started_at
            assert prompt.line_no
            assert prompt.file_name
            assert prompt.event

        stdouts = session.query(db_models.Stdout).all()  # type: ignore
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
    path = here.parent / 'example_script'
    return (path / 'script.py').read_text()


@pytest.fixture
async def run_nextline(db: DB, statement: str) -> None:
    nextline = Nextline(statement, trace_threads=True, trace_modules=True)
    async with write_db(nextline, db):
        async with nextline:
            await run_statement(nextline, statement)


@pytest.fixture
def db() -> Iterator[DB]:
    url = 'sqlite:///:memory:?check_same_thread=false'
    with DB(url=url) as db:
        yield db


async def run_statement(nextline: Nextline, statement: Optional[str] = None) -> None:
    await asyncio.sleep(0.01)
    await nextline.reset(statement=statement)
    await asyncio.sleep(0.01)
    task_control = asyncio.create_task(control(nextline))
    async with nextline.run_session():
        pass
    await task_control
    await asyncio.sleep(0.01)


async def control(nextline: Nextline) -> None:
    aiters = merge_aiters(nextline.subscribe_state(), nextline.subscribe_prompt_info())
    async for _, i in aiters:
        command: Optional[str] = None
        match i:
            case 'finished':
                break
            case PromptInfo(open=True, event='line', line_no=line_no):
                assert line_no is not None
                line = nextline.get_source_line(line_no=line_no, file_name=i.file_name)
                command = find_command(line) or 'next'
            case PromptInfo(open=True):
                command = 'next'
            case _:
                continue
        assert command is not None
        assert isinstance(i, PromptInfo)
        await asyncio.sleep(0.01)
        await nextline.send_pdb_command(command, i.prompt_no, i.trace_no)


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
