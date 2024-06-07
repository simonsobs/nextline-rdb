"""replace "run_no" with "run_id" in unique constraints

Revision ID: 8d24d9c2e9ba
Revises: 4dc6a93dfed8
Create Date: 2024-06-07 08:11:23.466742

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '8d24d9c2e9ba'
down_revision = '4dc6a93dfed8'
branch_labels = None
depends_on = None


def upgrade():
    # Disable the foreign key constraints during the migration.
    # https://alembic.sqlalchemy.org/en/latest/batch.html#dealing-with-referencing-foreign-keys
    op.execute('PRAGMA foreign_keys=OFF;')

    with op.batch_alter_table('trace', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_trace_run_no'), type_='unique')
        batch_op.create_unique_constraint(
            batch_op.f('uq_trace_run_id'), ['run_id', 'trace_no']
        )

    with op.batch_alter_table('prompt', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_prompt_run_no'), type_='unique')
        batch_op.create_unique_constraint(
            batch_op.f('uq_prompt_run_id'), ['run_id', 'prompt_no']
        )

    # Re-enable the foreign key constraints
    op.execute('PRAGMA foreign_keys=ON;')


def downgrade():
    op.execute('PRAGMA foreign_keys=OFF;')

    with op.batch_alter_table('trace', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_trace_run_id'), type_='unique')
        batch_op.create_unique_constraint(
            batch_op.f('uq_trace_run_no'), ['run_no', 'trace_no']
        )

    with op.batch_alter_table('prompt', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_prompt_run_id'), type_='unique')
        batch_op.create_unique_constraint(
            batch_op.f('uq_prompt_run_no'), ['run_no', 'prompt_no']
        )

    op.execute('PRAGMA foreign_keys=ON;')
