from pathlib import Path


import nextline_rdb

ALEMBIC_INI = str(Path(nextline_rdb.__file__).resolve().parent / 'alembic.ini')


assert Path(ALEMBIC_INI).is_file()
