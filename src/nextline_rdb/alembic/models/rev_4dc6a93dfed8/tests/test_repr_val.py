import datetime
import inspect
from enum import Enum

from hypothesis import given
from hypothesis import strategies as st

from nextline_rdb.utils.strategies import st_enum_type
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


@given(st.data())
def test_arbitrary_enum(data: st.DataObject) -> None:
    enum_type = data.draw(st_enum_type())
    item = data.draw(st.sampled_from(enum_type))
    repr_ = repr_val(item)

    # Add as a local variable so `eval` can find it.
    frame = inspect.currentframe()
    assert frame
    frame.f_locals[enum_type.__name__] = enum_type

    eval_ = eval(repr_)
    assert eval_ == item


@given(st.datetimes())
def test_datetimes(value: datetime.datetime) -> None:
    assert not is_timezone_aware(value)
    repr_ = repr_val(value)
    assert datetime  # need for eval
    assert eval(repr_) == value
