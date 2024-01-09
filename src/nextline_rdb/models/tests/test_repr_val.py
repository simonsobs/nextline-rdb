import datetime
from enum import Enum
from string import ascii_lowercase, ascii_uppercase

from hypothesis import given
from hypothesis import strategies as st

from nextline_rdb.utils.utc import is_timezone_aware

from .. import repr_val


@given(...)
def test_integers(value: int) -> None:
    repr_ = repr_val(value)
    assert eval(repr_) == value


@given(...)
def test_floats(value: float) -> None:
    repr_ = repr_val(value)
    eval_ = eval(repr_)
    if value != value:  # NaN
        assert eval_ != eval_
    else:
        assert eval_ == value


@given(...)
def test_text(value: str) -> None:
    repr_ = repr_val(value)
    assert eval(repr_) == value


class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3


@given(st.sampled_from(Color))
def test_enum(value: Color) -> None:
    repr_ = repr_val(value)
    assert eval(repr_) == value


@st.composite
def st_enum_type(draw: st.DrawFn):
    '''Generate an Enum type.

    >>> enum_type = st_enum_type().example()
    >>> list(enum_type)
    [...]

    Code based on:
    https://github.com/HypothesisWorks/hypothesis/issues/2693#issuecomment-823710924

    '''
    names_ = st.text(ascii_lowercase, min_size=1)
    names = st.builds(lambda x: x.capitalize(), names_).filter(str.isidentifier)
    values = st.lists(st.text(ascii_uppercase, min_size=1), min_size=1, unique=True)
    return draw(st.builds(Enum, names, values))


@given(st.data())
def test_arbitrary_enum(data: st.DataObject):
    enum_type = data.draw(st_enum_type())
    item = data.draw(st.sampled_from(enum_type))
    repr_ = repr_val(item)
    locals()[enum_type.__name__] = enum_type  # so eval can find the type
    eval_ = eval(repr_)
    assert eval_ == item


@given(st.datetimes())
def test_datetimes(value: datetime.datetime) -> None:
    assert not is_timezone_aware(value)
    repr_ = repr_val(value)
    assert datetime  # need for eval
    assert eval(repr_) == value
