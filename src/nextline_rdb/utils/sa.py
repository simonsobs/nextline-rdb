from typing import Any, TypeVar

from sqlalchemy import inspect, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

T = TypeVar('T', bound=DeclarativeBase)


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
