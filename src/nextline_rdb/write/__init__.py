__all__ = ['register']

from nextline import Nextline

from nextline_rdb.db import DB

from .write_run_table import WriteRunTable


def register(nextline: Nextline, db: DB) -> None:
    nextline.register(WriteRunTable(db=db))
