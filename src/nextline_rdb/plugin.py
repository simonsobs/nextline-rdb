from collections.abc import AsyncIterator, Mapping, MutableMapping
from logging import getLogger
from pathlib import Path
from typing import Optional

from apluggy import asynccontextmanager
from dynaconf import Dynaconf, Validator
from nextline import Nextline
from nextlinegraphql.hook import spec
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from . import models
from .db import AsyncDB
from .schema import Mutation, Query, Subscription
from .write import async_write_db

HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = HERE / 'default.toml'

assert DEFAULT_CONFIG_PATH.is_file()

PRELOAD = (str(DEFAULT_CONFIG_PATH),)
SETTINGS = ()
VALIDATORS = (Validator("DB.URL", must_exist=True, is_type_of=str),)


class Plugin:
    @spec.hookimpl
    def dynaconf_preload(self) -> Optional[tuple[str, ...]]:
        return PRELOAD

    @spec.hookimpl
    def dynaconf_settings_files(self) -> Optional[tuple[str, ...]]:
        return SETTINGS

    @spec.hookimpl
    def dynaconf_validators(self) -> Optional[tuple[Validator, ...]]:
        return VALIDATORS

    @spec.hookimpl
    def configure(self, settings: Dynaconf) -> None:
        self._url = settings.db['url']

    @spec.hookimpl
    def schema(self) -> tuple[type, type | None, type | None]:
        return (Query, Mutation, Subscription)

    @spec.hookimpl
    @asynccontextmanager
    async def lifespan(self, context: Mapping) -> AsyncIterator[None]:
        nextline = context['nextline']
        self._db = AsyncDB(self._url)
        async with self._db:
            await self._initialize_nextline(nextline)
            async with async_write_db(nextline, self._db):
                yield

    async def _initialize_nextline(self, nextline: Nextline) -> None:
        run_no, script = await self._last_run_no_and_script()
        if run_no is not None:
            run_no += 1
            if run_no >= nextline._init_options.run_no_start_from:
                nextline._init_options.run_no_start_from = run_no
        if script is not None:
            nextline._init_options.statement = script

    async def _last_run_no_and_script(self) -> tuple[Optional[int], Optional[str]]:
        async with self._db.session() as session:
            last_run = await self._last_run(session)
            if last_run is None:
                return None, None
            else:
                return last_run.run_no, last_run.script

    async def _last_run(self, session: AsyncSession) -> Optional[models.Run]:
        stmt = select(models.Run, func.max(models.Run.run_no))
        if model := (await session.execute(stmt)).scalar_one_or_none():
            return model
        else:
            logger = getLogger(__name__)
            msg = "No previous runs were found in the DB"
            logger.info(msg)
            return None

    @spec.hookimpl
    def update_strawberry_context(self, context: MutableMapping) -> None:
        context['db'] = self._db
