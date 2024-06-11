"""Migrate data

Populate the `trace_calls` table with the data from the `prompts` table.

Revision ID: 5a61f247dd07
Revises: f3edea6dbde2
Create Date: 2024-06-10 10:15:05.410008

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.orm.session import Session

from nextline_rdb.alembic.models.rev_f3edea6dbde2 import Prompt, TraceCall

# revision identifiers, used by Alembic.
revision = '5a61f247dd07'
down_revision = 'f3edea6dbde2'
branch_labels = None
depends_on = None


def upgrade():
    # Disable the foreign key constraints during the migration.
    # https://alembic.sqlalchemy.org/en/latest/batch.html#dealing-with-referencing-foreign-keys
    op.execute('PRAGMA foreign_keys=OFF;')

    with Session(bind=op.get_bind()) as session, session.begin():
        select_prompt = sa.select(Prompt)
        prompts = session.scalars(select_prompt)
        for i, prompt in enumerate(prompts):
            trace_call = TraceCall(
                trace_call_no=i + 1,
                started_at=prompt.started_at,
                file_name=prompt.file_name,
                line_no=prompt.line_no,
                event=prompt.event,
                ended_at=prompt.ended_at,
                run_id=prompt.run_id,
                trace_id=prompt.trace_id,
            )
            prompt.trace_call = trace_call
            session.add(trace_call)

    # Re-enable the foreign key constraints
    op.execute('PRAGMA foreign_keys=ON;')


def downgrade():
    op.execute('PRAGMA foreign_keys=OFF;')

    with Session(bind=op.get_bind()) as session, session.begin():
        select_trace_call = sa.select(TraceCall)
        trace_calls = session.scalars(select_trace_call)
        for trace_call in trace_calls:
            session.delete(trace_call)

    op.execute('PRAGMA foreign_keys=ON;')
