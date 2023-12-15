from pathlib import Path

import nextline_rdb

_PACKAGE_TOP = Path(nextline_rdb.__file__).resolve().parent
ALEMBIC_INI = str(_PACKAGE_TOP / 'alembic' / 'alembic.ini')


assert Path(ALEMBIC_INI).is_file()
