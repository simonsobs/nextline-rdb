from logging import getLogger
from typing import Any, TypeVar

from sqlalchemy import Select, inspect, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from .until import until_not_none

T = TypeVar('T', bound=DeclarativeBase)

# NOTE: Consider make this configurable.
DEFAULT_UNTIL_SCALAR_ONE_TIMEOUT = 60  # seconds


async def until_scalar_one(
    session: AsyncSession,
    stmt: Select[tuple[T]],
    timeout: float = DEFAULT_UNTIL_SCALAR_ONE_TIMEOUT,
) -> T:
    '''Execute the statement until it returns exactly one row.

    The statement is repeatedly executed while it returns no rows. An exception
    is raised if the statement returns more than one row.
    '''

    async def _f() -> T | None:
        return (await session.execute(stmt)).scalar_one_or_none()

    try:
        return await until_not_none(_f, timeout=timeout)
    except Exception:
        logger = getLogger(__name__)
        logger.exception('')
        raise


async def load_all(session: AsyncSession, model_base_class: type[T]) -> list[T]:
    '''All rows of all tables in the database.

    Sorted by the ORM class names and primary keys.
    '''
    objs = [
        m
        for c in all_declared_models_based_on(model_base_class)
        for m in (await session.scalars(select(c))).all()
    ]
    objs = sorted(objs, key=class_name_and_primary_keys_of)
    return objs


def all_declared_models_based_on(model_base_class: type[T]) -> list[type[T]]:
    '''The ORM classes inheriting from the base class.'''
    return [m.class_ for m in model_base_class.registry.mappers]


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
