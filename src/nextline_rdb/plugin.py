from collections.abc import AsyncIterator, Mapping, MutableMapping
from pathlib import Path
from typing import Optional

from apluggy import asynccontextmanager
from dynaconf import Dynaconf, Validator
from nextlinegraphql.hook import spec

from . import write
from .db import DB
from .init import initialize_nextline
from .schema import Mutation, Query, Subscription

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
        self.url = settings.db['url']

    @spec.hookimpl
    def schema(self) -> tuple[type, type | None, type | None]:
        return (Query, Mutation, Subscription)

    @spec.hookimpl
    @asynccontextmanager
    async def lifespan(self, context: Mapping) -> AsyncIterator[None]:
        nextline = context['nextline']
        async with DB(self.url) as db:
            self._db = db
            await initialize_nextline(nextline, db)
            write.register(nextline=nextline, db=self._db)
            yield

    @spec.hookimpl
    def update_strawberry_context(self, context: MutableMapping) -> None:
        context['db'] = self._db
