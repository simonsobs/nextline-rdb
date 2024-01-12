from collections.abc import Sized

from hypothesis import given
from hypothesis import strategies as st

from nextline_rdb.pagination import Sort, SortField
from nextline_rdb.utils.strategies import st_graphql_ints, st_none_or

from .models import Entity


def st_entity() -> st.SearchStrategy[Entity]:
    return st.builds(
        Entity,
        num=st_none_or(st_graphql_ints()),
        txt=st_none_or(st.text()),
    )


@st.composite
def st_sort(draw: st.DrawFn) -> Sort:
    FIELDS = ('id', 'num', 'txt')
    fields = draw(st.lists(st.sampled_from(FIELDS), max_size=len(FIELDS), unique=True))
    return [SortField(field, draw(st.booleans())) for field in fields]


@given(st_sort())
def test_st_sort(sort: Sort):
    # ic(sort)
    pass


def cmp(e1: Entity, e2: Entity, sort: Sort | None) -> int:
    '''A comparison function to be used as `comp_to_key(partial(cmp, sort=sort))`'''
    for f in sort or []:
        a = getattr(e1, f.field)
        b = getattr(e2, f.field)
        match a, b:
            case None, None:
                continue
            case None, _:
                return 1 if f.desc else -1
            case _, None:
                return -1 if f.desc else 1
            case a, b if a < b:
                return 1 if f.desc else -1
            case a, b if a > b:
                return -1 if f.desc else 1
            case _:
                pass
    return 0


def st_idx(items: Sized) -> st.SearchStrategy[int | None]:
    '''A strategy that generates an index of `items` or `None`'''
    return st_none_or(st.sampled_from(range(len(items)))) if items else st.none()


def st_length(max_value: int, allow_none: bool = True) -> st.SearchStrategy[int | None]:
    '''A strategy that generates a natural number <= `max_value` or `None`'''
    st_int = st.integers(min_value=0, max_value=max_value)
    return st_none_or(st_int) if allow_none else st_int
