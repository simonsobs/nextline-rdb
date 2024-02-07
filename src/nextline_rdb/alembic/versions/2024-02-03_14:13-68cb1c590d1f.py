"""migrate data

Revision ID: 68cb1c590d1f
Revises: 245c4152e8d7
Create Date: 2024-02-03 14:13:13.174733

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.orm.session import Session

from nextline_rdb.alembic.models.rev_245c4152e8d7 import CurrentScript, Script

# revision identifiers, used by Alembic.
revision = '68cb1c590d1f'
down_revision = '245c4152e8d7'
branch_labels = None
depends_on = None


def upgrade():
    with Session(bind=op.get_bind()) as session, session.begin():
        select_script = sa.select(Script).where(Script.current.is_(True))
        script = session.execute(select_script).scalar_one_or_none()
        if script is not None:
            current_script = CurrentScript(script_id=script.id)
            script.current = False
            session.add(current_script)


def downgrade():
    with Session(bind=op.get_bind()) as session, session.begin():
        select_current_script = sa.select(CurrentScript)
        current_script = session.execute(select_current_script).scalar_one_or_none()
        if current_script is not None:
            current_script.script.current = True
            session.delete(current_script)
