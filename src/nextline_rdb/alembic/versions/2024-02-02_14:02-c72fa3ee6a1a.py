"""ensure at most one current script

Revision ID: c72fa3ee6a1a
Revises: f9a742bb2297
Create Date: 2024-02-02 14:02:52.427179

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.orm.session import Session

from nextline_rdb.alembic.models.rev_6e3cf7d9b6bf import Script
from nextline_rdb.utils import mark_last

# revision identifiers, used by Alembic.
revision = 'c72fa3ee6a1a'
down_revision = 'f9a742bb2297'
branch_labels = None
depends_on = None


def upgrade():
    with Session(bind=op.get_bind()) as session:
        with session.begin():
            select_scripts = (
                sa.select(Script).where(Script.current.is_(True)).order_by(Script.id)
            )
            scripts = session.execute(select_scripts).scalars().all()
            if len(scripts) > 1:
                for last, script in mark_last(scripts):
                    if not last:
                        script.current = False


def downgrade():
    pass
