from collections.abc import AsyncIterator, Mapping, MutableMapping
from logging import getLogger
from pathlib import Path
from typing import Optional

from apluggy import PluginManager, asynccontextmanager
from dynaconf import Dynaconf, Validator
from nextlinegraphql.hook import spec
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import models
from .db import DB
from .schema import Mutation, Query, Subscription
from .write import write_db

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
        self._db = DB(settings.db['url'])
        self._db.start()

    @spec.hookimpl
    def initial_run_no(self) -> Optional[int]:
        with self._db.session() as session:
            last_run = self._last_run(session)
            if last_run is None:
                return None
            else:
                return last_run.run_no + 1

    @spec.hookimpl
    def initial_script(self) -> Optional[str]:
        with self._db.session() as session:
            last_run = self._last_run(session)
            if last_run is None:
                return None
            else:
                return last_run.script

    @spec.hookimpl
    def schema(self) -> tuple[type, type | None, type | None]:
        return (Query, Mutation, Subscription)

    def _last_run(self, session: Session) -> Optional[models.Run]:
        stmt = select(models.Run, func.max(models.Run.run_no))
        if model := session.execute(stmt).scalar_one_or_none():
            return model
        else:
            logger = getLogger(__name__)
            msg = "No previous runs were found in the DB"
            logger.info(msg)
            return None

    @spec.hookimpl
    @asynccontextmanager
    async def lifespan(
        self, hook: PluginManager, context: Mapping
    ) -> AsyncIterator[None]:
        nextline = context['nextline']
        run_no: int = max(
            hook.hook.initial_run_no(), default=nextline._init_options.run_no_start_from
        )
        script: str = [*hook.hook.initial_script(), nextline._init_options.statement][0]
        nextline._init_options.run_no_start_from = run_no
        nextline._init_options.statement = script
        async with write_db(nextline, self._db):
            yield

    @spec.hookimpl
    def update_strawberry_context(self, context: MutableMapping) -> None:
        context['db'] = self._db
