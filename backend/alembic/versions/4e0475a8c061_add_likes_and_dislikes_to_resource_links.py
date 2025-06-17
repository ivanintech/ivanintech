"""Add likes and dislikes to resource_links

Revision ID: 4e0475a8c061
Revises: 9f0346115888
Create Date: 2025-06-17 08:31:36.157035

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e0475a8c061'
down_revision: Union[str, None] = '9f0346115888'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to add likes and dislikes to resource_links."""
    op.add_column('resource_links', sa.Column('likes', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('resource_links', sa.Column('dislikes', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    """Downgrade schema to remove likes and dislikes from resource_links."""
    op.drop_column('resource_links', 'dislikes')
    op.drop_column('resource_links', 'likes')
