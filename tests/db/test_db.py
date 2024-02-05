from collections.abc import Callable
from typing import Any, TypeVar

import pytest
from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import inspect, select
from sqlalchemy.orm import DeclarativeBase

from nextline_rdb.db import DB
from nextline_rdb.utils import ensure_sync_url

from .models import Bar, Foo, Model, register_session_events

T = TypeVar('T', bound=DeclarativeBase)


def all_declared_models_based_on(model_base_class: type[T]) -> list[type[T]]:
    '''The ORM classes inheriting from the base class.'''
    return [m.class_ for m in model_base_class.registry.mappers]


MODEL_CLASSES = all_declared_models_based_on(Model)  # i.e., [Foo, Bar]


async def test_ensure_sync_url(tmp_url_factory: Callable[[], str]):
    url = tmp_url_factory()
    sync_url = ensure_sync_url(url)

    async with DB(url=sync_url) as db:
        assert db.url == url


async def test_fields():
    db = DB()
    assert db.url
    assert db.metadata
    assert db.engine

    async with db:
        assert db.session


@given(st.booleans())
async def test_migration_revision(use_migration: bool) -> None:
    async with DB(use_migration=use_migration) as db:
        if use_migration:
            assert db.migration_revision
        else:
            assert db.migration_revision is None


@given(st.lists(st.integers(min_value=0, max_value=4), min_size=0, max_size=4))
async def test_session_nested(tmp_url_factory: Callable[[], str], sizes: list[int]):
    url = tmp_url_factory()

    objs = [Foo(bars=[Bar() for _ in range(size)]) for size in sizes]

    async with DB(
        url=url,
        model_base_class=Model,
        use_migration=False,
        register_session_events=register_session_events,
    ) as db:
        async with db.session() as session:
            async with session.begin():
                session.add_all(objs)  # Related objects will be automatically added.
                added = list(session.new)
                assert set(objs) <= set(added)

            added = sorted(added, key=class_name_and_primary_keys_of)
            assert len(added) == sum(sizes) + len(sizes)

            repr_added = [repr(m) for m in added]

        async with db.session() as session:
            loaded = [
                m
                for c in MODEL_CLASSES
                for m in (await session.scalars(select(c))).all()
            ]
            loaded = sorted(loaded, key=class_name_and_primary_keys_of)
            repr_loaded = [repr(m) for m in loaded]

        assert repr_added == repr_loaded


@given(st.lists(st.integers(min_value=0, max_value=4), min_size=0, max_size=4))
async def test_session_begin(tmp_url_factory: Callable[[], str], sizes: list[int]):
    url = tmp_url_factory()

    objs = [Foo(bars=[Bar() for _ in range(size)]) for size in sizes]

    async with DB(
        url=url,
        model_base_class=Model,
        use_migration=False,
        register_session_events=register_session_events,
    ) as db:
        async with db.session.begin() as session:
            session.add_all(objs)  # Related objects will be automatically added.
            added = list(session.new)
            assert set(objs) <= set(added)

        added = sorted(added, key=class_name_and_primary_keys_of)
        assert len(added) == sum(sizes) + len(sizes)

        repr_added = [repr(m) for m in added]

        async with db.session() as session:
            loaded = [
                m
                for c in MODEL_CLASSES
                for m in (await session.scalars(select(c))).all()
            ]
            loaded = sorted(loaded, key=class_name_and_primary_keys_of)
            repr_loaded = [repr(m) for m in loaded]

        assert repr_added == repr_loaded


def class_name_and_primary_keys_of(instance: DeclarativeBase) -> tuple[Any, ...]:
    '''A tuple of the ORM class name followed by the primary key values.'''
    class_name = type(instance).__name__
    vals = primary_keys_of(instance)
    return (class_name,) + vals


def primary_keys_of(instance: DeclarativeBase) -> tuple[Any, ...]:
    '''A tuple of the primary key values.'''
    cls = type(instance)
    instance_mapper = inspect(cls)
    column_names = [attr.key for attr in instance_mapper.primary_key]
    values = tuple(getattr(instance, name) for name in column_names)
    return values


@pytest.fixture(scope='session')
def tmp_url_factory(tmp_path_factory: pytest.TempPathFactory) -> Callable[[], str]:
    def factory() -> str:
        dir = tmp_path_factory.mktemp('db')
        url = f'sqlite+aiosqlite:///{dir}/db.sqlite'
        return url

    return factory
