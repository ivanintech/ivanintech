"""Add server_default to updated_at in NewsItem

Revision ID: 9f0346115888
Revises: 2a7a5a062378
Create Date: 2025-06-15 21:40:50.306064

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f0346115888'
down_revision: Union[str, None] = '2a7a5a062378'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_index('ix_apscheduler_jobs_next_run_time', table_name='apscheduler_jobs')
    # op.drop_table('apscheduler_jobs')
    with op.batch_alter_table('news_items', schema=None) as batch_op:
        batch_op.alter_column('is_community',
                   existing_type=sa.BOOLEAN(),
                   nullable=False,
                   server_default='0')
        batch_op.alter_column('updated_at',
                   existing_type=sa.DATETIME(),
                   nullable=False,
                   server_default=sa.func.now())

    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('news_items', schema=None) as batch_op:
        batch_op.alter_column('updated_at',
                   existing_type=sa.DATETIME(),
                   nullable=True,
                   server_default=None)
        batch_op.alter_column('is_community',
                   existing_type=sa.BOOLEAN(),
                   nullable=True)

    op.create_table('apscheduler_jobs',
    sa.Column('id', sa.VARCHAR(length=191), nullable=False),
    sa.Column('next_run_time', sa.FLOAT(), nullable=True),
    sa.Column('job_state', sa.BLOB(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_apscheduler_jobs_next_run_time', 'apscheduler_jobs', ['next_run_time'], unique=False)
    # ### end Alembic commands ###
