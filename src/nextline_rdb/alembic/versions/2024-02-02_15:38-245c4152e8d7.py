"""add the table "current_script"

Revision ID: 245c4152e8d7
Revises: c72fa3ee6a1a
Create Date: 2024-02-02 15:38:18.902883

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '245c4152e8d7'
down_revision = 'c72fa3ee6a1a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('PRAGMA foreign_keys=OFF;')
    op.create_table(
        'current_script',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('script_id', sa.Integer(), nullable=False),
        sa.CheckConstraint('id = 1', name=op.f('ck_current_script_')),
        sa.ForeignKeyConstraint(
            ['script_id'],
            ['script.id'],
            name=op.f('fk_current_script_script_id_script'),
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_current_script')),
    )
    with op.batch_alter_table('current_script', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_current_script_id'), ['id'], unique=False)
    op.execute('PRAGMA foreign_keys=ON;')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('PRAGMA foreign_keys=OFF;')
    with op.batch_alter_table('current_script', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_current_script_id'))

    op.drop_table('current_script')
    op.execute('PRAGMA foreign_keys=ON;')
    # ### end Alembic commands ###
