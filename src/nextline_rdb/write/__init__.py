__all__ = ['register']

from nextline import Nextline

from nextline_rdb.db import DB

from .write_prompt_table import WritePromptTable
from .write_run_table import WriteRunTable
from .write_script_table import WriteScriptTable
from .write_stdout_table import WriteStdoutTable
from .write_trace_table import WriteTraceTable


def register(nextline: Nextline, db: DB) -> None:
    nextline.register(WriteRunTable(db=db))
    nextline.register(WriteScriptTable(db=db))
    nextline.register(WriteTraceTable(db=db))
    nextline.register(WritePromptTable(db=db))
    nextline.register(WriteStdoutTable(db=db))
