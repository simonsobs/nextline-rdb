from collections.abc import Sequence
from typing import Any, NamedTuple, Optional, Type, TypeVar

from sqlalchemy import ScalarResult, func, select
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
    select_model: Optional[Select[tuple[T]]] = None,
    sort: Optional[Sort] = None,
    before: Optional[_Id] = None,
    after: Optional[_Id] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> ScalarResult[T]:
    sort = sort or []

    if id_field not in {s.field for s in sort}:
        sort.append(SortField(id_field))

    order_by = [
        f.desc() if d else f
        for f, d in [(getattr(Model, s.field), s.desc) for s in sort]
    ]

    stmt = compose_statement(
        Model,
        id_field,
        select_model=select_model,
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
    Model: Type[T],
    id_field: str,
    *,
    select_model: Optional[Select[tuple[T]]] = None,
    order_by: Optional[Sequence[Any]] = None,
    before: Optional[_Id] = None,
    after: Optional[_Id] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> Select[tuple[T]]:
    '''Return a SQL select statement for pagination.

    Parameters
    ----------
    Model :
        The class of the ORM model to query.
    id_field :
        The name of the primary key field, e.g., 'id'.
    select_model : optional
        E.g., `select(Model).where(...)`. If not provided, `select(Model)` is used.
    order_by : optional
        The arguments to `row_number().over(order_by=...)` and `order_by()`. If
        not provided, the primary key field is used, e.g., `[Model.id]`.
    before : optional
        As in the GraphQL Cursor Connections Specification [1].
    after : optional
        As in the GraphQL Cursor Connections Specification [1].
    first : optional
        As in the GraphQL Cursor Connections Specification [1].
    last : optional
        As in the GraphQL Cursor Connections Specification [1].

    Returns
    -------
    stmt
        The composed select statement for pagination.

    Raises
    ------
    ValueError
        If both before/last and after/first parameters are provided.

    References
    ----------
    .. [1] https://relay.dev/graphql/connections.htm
    '''

    forward = (after is not None) or (first is not None)
    backward = (before is not None) or (last is not None)

    if forward and backward:
        raise ValueError('Only either after/first or before/last is allowed')

    if select_model is None:
        select_model = select(Model)

    if not order_by:
        # E.g., [T.id]
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
