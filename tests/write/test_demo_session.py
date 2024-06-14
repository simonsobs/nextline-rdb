import asyncio

from sqlalchemy import MetaData, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from nextline_rdb.db import DB
from nextline_rdb.models import NAMING_CONVENTION, ReprMixin

metadata = MetaData(naming_convention=dict(NAMING_CONVENTION))


class Model(ReprMixin, DeclarativeBase):
    metadata = metadata


class Entity(Model):
    __tablename__ = 'entity'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    num: Mapped[int | None]
    txt: Mapped[str | None]


async def test_session() -> None:
    '''Show changes in one session are visible in another session.'''
    async with DB(model_base_class=Model, use_migration=False) as db:
        first_read = asyncio.Event()
        written = asyncio.Event()

        async def write() -> None:
            '''Insert an entry after the other task reads once.'''
            await first_read.wait()
            async with db.session.begin() as session:
                entity = Entity(num=1, txt='one')
                session.add(entity)

            written.set()

        async def read() -> None:
            '''Look for the entry in a single session before and after it is inserted.'''
            async with db.session.begin() as session:
                stmt = select(Entity)
                entity = (await session.execute(stmt)).scalar_one_or_none()
                assert entity is None  # Not found

                first_read.set()
                await written.wait()

                entity = (await session.execute(stmt)).scalar_one_or_none()
                assert entity is not None  # Found. Unnecessary to enter a new session.

        await asyncio.gather(write(), read())
