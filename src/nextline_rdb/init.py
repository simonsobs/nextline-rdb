from logging import getLogger
from typing import Optional

from nextline import Nextline
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from .db import DB
from .models import CurrentScript, Run


async def initialize_nextline(nextline: Nextline, db: DB) -> None:
    run_no = await _last_run_no(db)
    if run_no is not None:
        run_no += 1
        if run_no >= nextline._init_options.run_no_start_from:
            nextline._init_options.run_no_start_from = run_no
    script = await _current_script(db)
    if script is not None:
        nextline._init_options.statement = script


async def _last_run_no(db: DB) -> Optional[int]:
    async with db.session() as session:
        stmt = select(Run, func.max(Run.run_no))
        if run := (await session.execute(stmt)).scalar_one_or_none():
            return run.run_no
        logger = getLogger(__name__)
        msg = 'No previous runs were found in the DB'
        logger.info(msg)
        return None


async def _current_script(db: DB) -> Optional[str]:
    async with db.session() as session:
        stmt = select(CurrentScript).options(selectinload(CurrentScript.script))
        if current_script := (await session.execute(stmt)).scalar_one_or_none():
            return current_script.script.script
        logger = getLogger(__name__)
        msg = 'No current scripts were found in the DB'
        logger.info(msg)
        return None
