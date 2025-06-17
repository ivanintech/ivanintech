"""Merge multiple heads

Revision ID: 90eb69a0f500
Revises: 4e0475a8c061
Create Date: 2025-06-17 08:46:35.152414

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '90eb69a0f500'
down_revision: Union[str, None] = '4e0475a8c061'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
