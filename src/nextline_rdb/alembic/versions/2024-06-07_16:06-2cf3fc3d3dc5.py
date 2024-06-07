"""Delete "run_no" and "trace_no" from "stdout"

Revision ID: 2cf3fc3d3dc5
Revises: ab0fe7b96033
Create Date: 2024-06-07 16:06:08.458800

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '2cf3fc3d3dc5'
down_revision = 'ab0fe7b96033'
branch_labels = None
depends_on = None


def upgrade():
    # Disable the foreign key constraints during the migration.
    # https://alembic.sqlalchemy.org/en/latest/batch.html#dealing-with-referencing-foreign-keys
    op.execute('PRAGMA foreign_keys=OFF;')

    with op.batch_alter_table('stdout', schema=None) as batch_op:
        batch_op.drop_column('run_no')
        batch_op.drop_column('trace_no')

    # Re-enable the foreign key constraints
    op.execute('PRAGMA foreign_keys=ON;')


def downgrade():
    op.execute('PRAGMA foreign_keys=OFF;')

    with op.batch_alter_table('stdout', schema=None) as batch_op:
        batch_op.add_column(sa.Column('trace_no', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('run_no', sa.INTEGER(), nullable=True))

    op.execute(
        '''
        UPDATE stdout
        SET run_no = (SELECT run_no FROM run WHERE run.id = stdout.run_id),
            trace_no = (SELECT trace_no FROM trace WHERE trace.id = stdout.trace_id)
    '''
    )

    with op.batch_alter_table('stdout', schema=None) as batch_op:
        batch_op.alter_column('trace_no', nullable=True)
        batch_op.alter_column('run_no', nullable=True)

    op.execute('PRAGMA foreign_keys=ON;')
