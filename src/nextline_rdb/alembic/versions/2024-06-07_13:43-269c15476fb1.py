"""Delete "run_no" from "trace"

Revision ID: 269c15476fb1
Revises: 8d24d9c2e9ba
Create Date: 2024-06-07 13:43:16.746754

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '269c15476fb1'
down_revision = '8d24d9c2e9ba'
branch_labels = None
depends_on = None


def upgrade():
    # Disable the foreign key constraints during the migration.
    # https://alembic.sqlalchemy.org/en/latest/batch.html#dealing-with-referencing-foreign-keys
    op.execute('PRAGMA foreign_keys=OFF;')

    with op.batch_alter_table('trace', schema=None) as batch_op:
        batch_op.drop_column('run_no')

    # Re-enable the foreign key constraints
    op.execute('PRAGMA foreign_keys=ON;')


def downgrade():
    op.execute('PRAGMA foreign_keys=OFF;')

    with op.batch_alter_table('trace', schema=None) as batch_op:
        batch_op.add_column(sa.Column('run_no', sa.Integer(), nullable=True))

    op.execute(
        '''
        UPDATE trace
        SET run_no = (SELECT run_no FROM run WHERE run.id = trace.run_id)
    '''
    )

    with op.batch_alter_table('trace', schema=None) as batch_op:
        batch_op.alter_column('run_no', nullable=False)

    # ### end Alembic commands ###

    op.execute('PRAGMA foreign_keys=ON;')
