"""Delete "event", "line_no", and "file_name" from "prompt"

Revision ID: 15003e123b98
Revises: f433a0a15c7e
Create Date: 2024-06-10 12:02:52.852500

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '15003e123b98'
down_revision = 'f433a0a15c7e'
branch_labels = None
depends_on = None


def upgrade():
    # Disable the foreign key constraints during the migration.
    # https://alembic.sqlalchemy.org/en/latest/batch.html#dealing-with-referencing-foreign-keys
    op.execute('PRAGMA foreign_keys=OFF;')

    with op.batch_alter_table('prompt', schema=None) as batch_op:
        batch_op.drop_column('event')
        batch_op.drop_column('line_no')
        batch_op.drop_column('file_name')

    # Re-enable the foreign key constraints
    op.execute('PRAGMA foreign_keys=ON;')


def downgrade():
    op.execute('PRAGMA foreign_keys=OFF;')

    with op.batch_alter_table('prompt', schema=None) as batch_op:
        batch_op.add_column(sa.Column('file_name', sa.VARCHAR(), nullable=True))
        batch_op.add_column(sa.Column('line_no', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('event', sa.VARCHAR(), nullable=True))

    op.execute(
        '''
        UPDATE prompt
        SET file_name = (SELECT file_name FROM trace_call WHERE
            trace_call.id = prompt.trace_call_id),
            line_no = (SELECT line_no FROM trace_call WHERE
            trace_call.id = prompt.trace_call_id),
            event = (SELECT event FROM trace_call WHERE
            trace_call.id = prompt.trace_call_id)
        '''
    )

    with op.batch_alter_table('prompt', schema=None) as batch_op:
        batch_op.alter_column('event', nullable=False)

    # ### end Alembic commands ###

    op.execute('PRAGMA foreign_keys=ON;')
