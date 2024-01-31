"""migrate data

Revision ID: cafceacada62
Revises: 6e3cf7d9b6bf
Create Date: 2024-01-29 16:33:19.473453

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.orm.session import Session

from nextline_rdb.alembic.models.rev_6e3cf7d9b6bf import Run, Script
from nextline_rdb.utils import mark_last

# revision identifiers, used by Alembic.
revision = 'cafceacada62'
down_revision = '6e3cf7d9b6bf'
branch_labels = None
depends_on = None


def upgrade():
    with Session(bind=op.get_bind()) as session:
        with session.begin():
            session.query(Script).delete()

        with session.begin():
            select_runs = sa.select(Run).order_by(Run.run_no)
            runs = session.execute(select_runs).scalars().all()
            scripts = list[Script]()
            for last, run in mark_last(runs):
                if run.script_old is None:
                    continue
                script = Script(script=run.script_old, current=last)
                scripts += [script]
                run.script = script
                run.script_old = None


def downgrade():
    with Session(bind=op.get_bind()) as session:
        with session.begin():
            select_scripts = sa.select(Script).order_by(Script.id)
            scripts = session.execute(select_scripts).scalars().all()
            for script in scripts:
                for run in script.runs:
                    run.script_old = script.script
                session.delete(script)
