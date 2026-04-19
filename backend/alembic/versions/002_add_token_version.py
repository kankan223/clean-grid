"""Add token version to users

Revision ID: 002
Revises: 001
Create Date: 2026-04-19 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('token_version', sa.Integer(), nullable=False, server_default=sa.text('0'), comment='JWT token rotation version')
    )
    op.alter_column('users', 'token_version', server_default=None)


def downgrade() -> None:
    op.drop_column('users', 'token_version')