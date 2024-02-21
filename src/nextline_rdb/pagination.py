from collections.abc import Sequence
from typing import Any, NamedTuple, Optional, Type, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, aliased, selectinload
from sqlalchemy.sql.selectable import Select

# import sqlparse


# def format_sql(sql):
#     return sqlparse.format(str(sql), reindent=True, keyword_case='upper')


class SortField(NamedTuple):
    field: str
    desc: bool = False


Sort = list[SortField]

_Id = TypeVar('_Id')

T = TypeVar('T', bound=DeclarativeBase)


async def load_models(
    session: AsyncSession,
    Model: Type[T],
    id_field: str,
    *,
    sort: Optional[Sort] = None,
    before: Optional[_Id] = None,
    after: Optional[_Id] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
):
    select_model = select(Model)

    sort = sort or []

    if id_field not in {s.field for s in sort}:
        sort.append(SortField(id_field))

    order_by = [
        f.desc() if d else f
        for f, d in [(getattr(Model, s.field), s.desc) for s in sort]
    ]

    stmt = compose_statement(
        select_model,
        Model,
        id_field,
        order_by=order_by,
        before=before,
        after=after,
        first=first,
        last=last,
    )

    # TODO: Make this optional
    stmt = stmt.options(selectinload('*'))

    models = await session.scalars(stmt)
    return models


def compose_statement(
    select_model: Select[tuple[T]],
    Model: Type[T],
    id_field: str,
    *,
    order_by: Optional[Sequence[Any]] = None,
    before: Optional[_Id] = None,
    after: Optional[_Id] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> Select[tuple[T]]:
    '''Return a SELECT statement object to be given to session.scalars'''

    forward = (after is not None) or (first is not None)
    backward = (before is not None) or (last is not None)

    if forward and backward:
        raise ValueError('Only either after/first or before/last is allowed')

    if not order_by:
        order_by = [getattr(Model, id_field)]

    if not (forward or backward):
        return select_model.order_by(*order_by)

    cursor = after if forward else before
    limit = first if forward else last

    # A CTE (Common Table Expression) with a row_number column
    cte = select_model.add_columns(
        func.row_number().over(order_by=order_by).label('row_number')
    ).cte()

    Alias = aliased(Model, cte)
    stmt = select(Alias, cte.c.row_number).select_from(cte)

    if cursor is not None:
        # A subquery to find the row_number at the cursor
        stmt_subq = select(cte.c.row_number.label('at_cursor'))
        stmt_subq = stmt_subq.where(getattr(cte.c, id_field) == cursor)
        subq = stmt_subq.subquery()

        # Select rows after or before (if backward) the cursor
        stmt = stmt.select_from(subq)
        if backward:
            stmt = stmt.where(cte.c.row_number < subq.c.at_cursor)
        else:
            stmt = stmt.where(cte.c.row_number > subq.c.at_cursor)

    if limit is not None:
        # Specify the maximum number of rows to return
        if backward:
            stmt = stmt.order_by(cte.c.row_number.desc())
        else:
            stmt = stmt.order_by(cte.c.row_number)
        stmt = stmt.limit(limit)

    # Select only the model (not the row_number) and ensure the order
    cte = stmt.cte()
    Alias = aliased(Model, cte)
    stmt = select(Alias).select_from(cte)
    stmt = stmt.order_by(cte.c.row_number)

    return stmt
