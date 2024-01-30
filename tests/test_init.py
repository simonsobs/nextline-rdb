from hypothesis import given
from nextline import Nextline

from nextline_rdb.db import DB
from nextline_rdb.init import initialize_nextline
from nextline_rdb.models import Run
from nextline_rdb.models.strategies import st_model_run_list
from nextline_rdb.utils.strategies import st_python_scripts


@given(
    runs=st_model_run_list(generate_traces=False, min_size=0, max_size=2),
    default_statement=st_python_scripts(),
)
async def test_initialize_nextline(runs: list[Run], default_statement: str) -> None:
    last_run = runs[-1] if runs else None

    expected_run_no = last_run.run_no + 1 if last_run else 1

    current_scripts = [r.script.script for r in runs if r.script and r.script.current]
    expected_statement = (
        default_statement if not current_scripts else current_scripts[-1]
    )

    nextline = Nextline(statement=default_statement)

    async with DB() as db:
        async with db.session.begin() as session:
            session.add_all(runs)
        await initialize_nextline(nextline, db)

    init_options = nextline._init_options

    assert init_options.run_no_start_from == expected_run_no
    assert init_options.statement == expected_statement
