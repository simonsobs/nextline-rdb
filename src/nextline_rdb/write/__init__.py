__all__ = ['register']

from nextline import Nextline

from nextline_rdb.db import DB

from .write_run_table import WriteRunTable
from .write_trace_table import WriteTraceTable


def register(nextline: Nextline, db: DB) -> None:
    nextline.register(WriteRunTable(db=db))
    nextline.register(WriteTraceTable(db=db))
