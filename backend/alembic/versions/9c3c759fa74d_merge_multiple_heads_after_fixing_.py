"""Merge multiple heads after fixing history

Revision ID: 9c3c759fa74d
Revises: 9f6654de1ec5, e9f574a02116
Create Date: 2025-06-18 13:37:14.170609

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9c3c759fa74d'
down_revision: Union[str, None] = ('9f6654de1ec5', 'e9f574a02116')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
