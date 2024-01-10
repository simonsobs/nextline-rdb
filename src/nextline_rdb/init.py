from logging import getLogger
from typing import Optional

from nextline import Nextline
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from . import models
from .db import DB


async def initialize_nextline(nextline: Nextline, db: DB) -> None:
    run_no, script = await _last_run_no_and_script(db)
    if run_no is not None:
        run_no += 1
        if run_no >= nextline._init_options.run_no_start_from:
            nextline._init_options.run_no_start_from = run_no
    if script is not None:
        nextline._init_options.statement = script


async def _last_run_no_and_script(db: DB) -> tuple[Optional[int], Optional[str]]:
    async with db.session() as session:
        last_run = await _last_run(session)
        if last_run is None:
            return None, None
        else:
            return last_run.run_no, last_run.script


async def _last_run(session: AsyncSession) -> Optional[models.Run]:
    stmt = select(models.Run, func.max(models.Run.run_no))
    if model := (await session.execute(stmt)).scalar_one_or_none():
        return model
    else:
        logger = getLogger(__name__)
        msg = "No previous runs were found in the DB"
        logger.info(msg)
        return None
