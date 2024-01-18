from typing import cast

import strawberry
from sqlalchemy import select
from strawberry.types import Info

from nextline_rdb.db import DB
from nextline_rdb.models import Run


async def mutate_delete_runs(info: Info, ids: list[int]) -> list[int]:
    db = cast(DB, info.context['db'])
    async with db.session.begin() as session:
        stmt = select(Run).filter(Run.id.in_(ids))
        runs = (await session.execute(stmt)).scalars().all()
        # ic(runs)
        for run in runs:
            await session.delete(run)
        ret = [run.id for run in runs]
    return ret


@strawberry.type
class MutationRDB:
    delete_runs: list[int] = strawberry.field(resolver=mutate_delete_runs)


@strawberry.type
class Mutation:
    @strawberry.field
    async def rdb(self) -> MutationRDB:
        return MutationRDB()
