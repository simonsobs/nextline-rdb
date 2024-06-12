import asyncio

import pytest
from hypothesis import given
from hypothesis import strategies as st
from nextline.utils import aiterable

from nextline_rdb.utils import UntilNotNoneTimeout, until_not_none


@given(st.data())
async def test_return(data: st.DataObject) -> None:
    val = data.draw(st.text())
    nones = data.draw(st.lists(st.none(), max_size=10))
    ret = nones + [val]
    func = aiterable(ret).__anext__
    assert (await until_not_none(func)) == val


async def test_timeout() -> None:
    async def gen_none():
        while True:
            await asyncio.sleep(0)
            yield None

    g = gen_none()
    func = g.__anext__
    with pytest.raises(UntilNotNoneTimeout):
        await until_not_none(func, timeout=0.001)


@pytest.mark.timeout(5)
async def test_timeout_never_return() -> None:
    async def func():
        while True:
            await asyncio.sleep(0)

    with pytest.raises(UntilNotNoneTimeout):
        await until_not_none(func, timeout=0.001)
