"""Add relevance_rating to news_items and clean up old columns

Revision ID: e9f574a02116
Revises: b2711c6722c6
Create Date: 2025-06-18 12:55:15.323269

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e9f574a02116'
down_revision: Union[str, None] = 'b2711c6722c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('news_items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('relevance_rating', sa.Integer(), nullable=True))
        batch_op.drop_column('relevance_score')
        batch_op.drop_column('star_rating')


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('news_items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('star_rating', sa.FLOAT(), nullable=True))
        batch_op.add_column(sa.Column('relevance_score', sa.INTEGER(), nullable=True))
        batch_op.drop_column('relevance_rating')
