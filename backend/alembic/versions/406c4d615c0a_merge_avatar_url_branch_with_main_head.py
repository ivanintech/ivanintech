"""Merge avatar_url branch with main head

Revision ID: 406c4d615c0a
Revises: b5a3e9c8d7f6, b43b5e23b9e3
Create Date: 2025-06-21 01:21:59.336818

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '406c4d615c0a'
down_revision: Union[str, None] = ('b5a3e9c8d7f6', 'b43b5e23b9e3')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
