from typing import NamedTuple, Optional, Type, TypeVar, cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, aliased, selectinload
from sqlalchemy.sql.expression import literal
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

    stmt = compose_statement(
        select_model,
        Model,
        id_field,
        sort=sort,
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
    sort: Optional[Sort] = None,
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

    sort = sort or []

    if id_field not in [s.field for s in sort]:
        sort.append(SortField(id_field))

    order_by = [
        f.desc() if d else f
        for f, d in [(getattr(Model, s.field), s.desc) for s in sort]
    ]

    if not (forward or backward):
        return select_model.order_by(*order_by)

    cursor = after if forward else before
    limit = first if forward else last

    cte = select_model.add_columns(
        func.row_number().over(order_by=order_by).label('row_number')
    ).cte()
    Alias = aliased(Model, cte)
    stmt = select(Alias, cte.c.row_number).select_from(cte)

    if cursor is not None:
        subq = select(cte.c.row_number.label('cursor'))
        subq = subq.where(getattr(cte.c, id_field) == cursor)
        subq = cast(Select[tuple], subq.subquery())

        stmt = stmt.join(subq, literal(True))  # type: ignore # cartesian product
        if backward:
            stmt = stmt.where(cte.c.row_number < subq.c.cursor)
        else:
            stmt = stmt.where(cte.c.row_number > subq.c.cursor)

    if backward:
        stmt = stmt.order_by(cte.c.row_number.desc())

    if limit is not None:
        stmt = stmt.limit(limit)

    # Select only the model (not the row_number) and ensure the order
    cte = stmt.cte()
    Alias = aliased(Model, cte)
    stmt = select(Alias).select_from(cte)
    stmt = stmt.order_by(cte.c.row_number)

    return stmt
