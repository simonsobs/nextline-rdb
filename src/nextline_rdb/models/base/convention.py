# Constraints naming conventions
#
# SQLAlchemy 2 Doc:
# https://docs.sqlalchemy.org/en/20/core/constraints.html#configuring-constraint-naming-conventions
#
# About the change on 'ck':
# https://stackoverflow.com/a/56000475/7309855
#
# Equivalent code in ProductDB:
# https://github.com/simonsobs/acondbs/blob/7b4e5ab967ce/acondbs/db/sa.py
NAMING_CONVENTION = {
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    # 'ck': 'ck_%(table_name)s_%(constraint_name)s',
    'ck': 'ck_%(table_name)s_%(column_0_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s',
}
