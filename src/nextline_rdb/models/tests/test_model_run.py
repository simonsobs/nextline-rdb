from hypothesis import Phase, given, settings
from sqlalchemy import select

from nextline_rdb.db import DB

from .. import Model, Run, Trace
from ..strategies import st_model_run


@settings(phases=(Phase.generate,))  # Avoid shrinking
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
            select_traces = select(Trace)
            trace = (await session.execute(select_traces)).scalar_one_or_none()
            assert not trace
