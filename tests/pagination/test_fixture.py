from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Entity


async def test_sample(session: AsyncSession):
    Model = Entity
    stmt = select(Model)
    models = await session.scalars(stmt)
    assert 10 == len(models.all())
