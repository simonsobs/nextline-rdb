import keyword
from enum import Enum
from string import ascii_lowercase, ascii_uppercase

from hypothesis import strategies as st


@st.composite
def st_enum_type(draw: st.DrawFn) -> type[Enum]:
    '''Generate an Enum type.

    Examples
    --------

    Draw an Enum type with Hypothesis:
    >>> enum_type = st_enum_type().example()

    >>> import inspect
    >>> inspect.isclass(enum_type)
    True

    >>> issubclass(enum_type, Enum)
    True

    >>> len(list(enum_type)) > 0
    True

    Draw an item.
    >>> item = st.sampled_from(enum_type).example()
    >>> item in enum_type
    True

    >>> isinstance(item, enum_type)
    True


    Code based on:
    https://github.com/HypothesisWorks/hypothesis/issues/2693#issuecomment-823710924

    '''
    names_ = st.text(ascii_lowercase, min_size=1)
    names = (
        st.builds(lambda x: x.capitalize(), names_)
        .filter(str.isidentifier)
        .filter(lambda x: not keyword.iskeyword(x))
    )
    values = st.lists(st.text(ascii_uppercase, min_size=1), min_size=1, unique=True)
    return draw(st.builds(Enum, names, values))  # type: ignore
