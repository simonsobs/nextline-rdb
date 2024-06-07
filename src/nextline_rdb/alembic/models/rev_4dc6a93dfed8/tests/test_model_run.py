import datetime

from hypothesis import given
from sqlalchemy import select

from nextline_rdb.db import DB

from .. import Model, Run
from ..strategies import st_model_run


@given(run=st_model_run(generate_traces=False))
async def test_repr(run: Run):
    async with DB(use_migration=False, model_base_class=Model) as db:
        async with db.session.begin() as session:
            session.add(run)

        async with db.session() as session:
            rows = await session.scalars(select(Run))
            for row in rows:
                repr_ = repr(row)
                assert Run, datetime  # type: ignore[truthy-function]
                assert repr_ == repr(eval(repr_))


@given(run=st_model_run(generate_traces=True))
async def test_cascade(run: Run):
    async with DB(use_migration=False, model_base_class=Model) as db:
        async with db.session.begin() as session:
            session.add(run)

        async with db.session.begin() as session:
            select_run = select(Run)
            run = (await session.execute(select_run)).scalar_one()
            await session.delete(run)

        async with db.session() as session:
            select_traces = select(Run)
            traces = (await session.execute(select_traces)).scalars().all()
            assert not traces
