"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
import sqlalchemy as sa
from alembic import op
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade():
    # Disable the foreign key constraints during the migration.
    # https://alembic.sqlalchemy.org/en/latest/batch.html#dealing-with-referencing-foreign-keys
    op.execute('PRAGMA foreign_keys=OFF;')

    ${upgrades if upgrades else "pass"}
    
    # Re-enable the foreign key constraints
    op.execute('PRAGMA foreign_keys=ON;')


def downgrade():
    op.execute('PRAGMA foreign_keys=OFF;')

    ${downgrades if downgrades else "pass"}

    op.execute('PRAGMA foreign_keys=ON;')
