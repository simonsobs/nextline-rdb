"""init

Revision ID: de90b787e92f
Revises:
Create Date: 2022-03-14 14:00:25.218755

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'de90b787e92f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'hello',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('message', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_hello_id'), 'hello', ['id'], unique=False)
    op.create_table(
        'run',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('run_no', sa.Integer(), nullable=False),
        sa.Column('state', sa.String(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('script', sa.Text(), nullable=True),
        sa.Column('exception', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('run_no'),
    )
    op.create_index(op.f('ix_run_id'), 'run', ['id'], unique=False)
    op.create_table(
        'stdout',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('run_no', sa.Integer(), nullable=False),
        sa.Column('text', sa.String(), nullable=True),
        sa.Column('written_at', sa.DateTime(), nullable=True),
        sa.Column('run_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['run_id'],
            ['run.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_stdout_id'), 'stdout', ['id'], unique=False)
    op.create_table(
        'trace',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('run_no', sa.Integer(), nullable=False),
        sa.Column('trace_no', sa.Integer(), nullable=False),
        sa.Column('state', sa.String(), nullable=False),
        sa.Column('thread_no', sa.Integer(), nullable=False),
        sa.Column('task_no', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('run_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['run_id'],
            ['run.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('run_no', 'trace_no'),
    )
    op.create_index(op.f('ix_trace_id'), 'trace', ['id'], unique=False)
    op.create_table(
        'prompt',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('run_no', sa.Integer(), nullable=False),
        sa.Column('trace_no', sa.Integer(), nullable=False),
        sa.Column('prompt_no', sa.Integer(), nullable=False),
        sa.Column('open', sa.Boolean(), nullable=False),
        sa.Column('event', sa.String(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('file_name', sa.String(), nullable=True),
        sa.Column('line_no', sa.Integer(), nullable=True),
        sa.Column('stdout', sa.String(), nullable=True),
        sa.Column('command', sa.String(), nullable=True),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('run_id', sa.Integer(), nullable=False),
        sa.Column('trace_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['run_id'],
            ['run.id'],
        ),
        sa.ForeignKeyConstraint(
            ['trace_id'],
            ['trace.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('run_no', 'prompt_no'),
    )
    op.create_index(op.f('ix_prompt_id'), 'prompt', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_prompt_id'), table_name='prompt')
    op.drop_table('prompt')
    op.drop_index(op.f('ix_trace_id'), table_name='trace')
    op.drop_table('trace')
    op.drop_index(op.f('ix_stdout_id'), table_name='stdout')
    op.drop_table('stdout')
    op.drop_index(op.f('ix_run_id'), table_name='run')
    op.drop_table('run')
    op.drop_index(op.f('ix_hello_id'), table_name='hello')
    op.drop_table('hello')
    # ### end Alembic commands ###
