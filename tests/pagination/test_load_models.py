from functools import cmp_to_key, partial

from hypothesis import given, note
from hypothesis import strategies as st

from nextline_rdb.db import DB
from nextline_rdb.pagination import load_models
from nextline_rdb.utils.strategies import st_none_or

from .funcs import cmp, st_entity, st_idx, st_length, st_sort
from .models import Base, Entity


@given(st.data())
async def test_all(data: st.DataObject):
    n_max = 10

    entities = data.draw(st.lists(st_entity(), min_size=0, max_size=n_max))
    sort = data.draw(st_none_or(st_sort()), label='sort')

    async with DB(model_base_class=Base, use_migration=False) as db:
        async with db.session.begin() as session:
            session.add_all(entities)

        note(f'entities={entities}')

        ordered = sorted(entities, key=cmp_to_key(partial(cmp, sort=sort)))

        expected = ordered[:]

        async with db.session() as session:
            models = (await load_models(session, Entity, 'id', sort=sort)).all()

    assert repr(models) == repr(expected)


@given(st.data())
async def test_forward(data: st.DataObject):
    n_max = 10

    entities = data.draw(st.lists(st_entity(), min_size=0, max_size=n_max))
    sort = data.draw(st_none_or(st_sort()), label='sort')

    async with DB(model_base_class=Base, use_migration=False) as db:
        async with db.session.begin() as session:
            session.add_all(entities)

        note(f'entities={entities}')

        ordered = sorted(entities, key=cmp_to_key(partial(cmp, sort=sort)))

        after_idx = data.draw(st_idx(ordered), label='after')
        after = ordered[after_idx].id if after_idx is not None else None
        first = data.draw(
            st_length(len(ordered), allow_none=after_idx is not None), label='first'
        )
        note(f'after={after}, first={first}')

        start = after_idx + 1 if after_idx is not None else None
        end = first if start is None else (None if first is None else (start + first))
        note(f'start={start}, end={end}')

        expected = ordered[slice(start, end, None)]

        async with db.session() as session:
            models = (
                await load_models(
                    session, Entity, 'id', sort=sort, after=after, first=first
                )
            ).all()

    assert repr(models) == repr(expected)


@given(st.data())
async def test_backward(data: st.DataObject):
    n_max = 10

    entities = data.draw(st.lists(st_entity(), min_size=0, max_size=n_max))
    sort = data.draw(st_none_or(st_sort()), label='sort')

    async with DB(model_base_class=Base, use_migration=False) as db:
        async with db.session.begin() as session:
            session.add_all(entities)

        note(f'entities={entities}')

        ordered = sorted(entities, key=cmp_to_key(partial(cmp, sort=sort)))

        before_idx = data.draw(st_idx(ordered), label='before')
        before = ordered[before_idx].id if before_idx is not None else None
        last = data.draw(
            st_length(len(ordered), allow_none=before_idx is not None), label='last'
        )
        note(f'before={before}, last={last}')

        end = before_idx if before_idx is not None else None
        start = (
            None
            if last is None
            else (len(ordered) - last if end is None else max(end - last, 0))
        )
        note(f'start={start}, end={end}')

        expected = ordered[slice(start, end, None)]

        async with db.session() as session:
            models = (
                await load_models(
                    session, Entity, 'id', sort=sort, before=before, last=last
                )
            ).all()

    assert repr(models) == repr(expected)
