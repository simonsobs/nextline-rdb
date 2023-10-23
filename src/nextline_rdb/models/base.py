from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# https://docs.sqlalchemy.org/en/14/core/constraints.html#configuring-a-naming-convention-for-a-metadata-collection
# https://github.com/simonsobs/acondbs/blob/7b4e5ab967ce/acondbs/db/sa.py
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    # "ck": "ck_%(table_name)s_%(constraint_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    metadata = metadata
