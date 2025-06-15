"""Crear tabla resource_votes y reconciliar esquema

Revision ID: 1816b573ea9a
Revises: a76de84ab972
Create Date: 2025-06-14 17:46:03.246355

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '1816b573ea9a'
down_revision: Union[str, None] = 'a76de84ab972'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Define el tipo ENUM, indicando que no debe crearlo automáticamente.
    votetype = postgresql.ENUM('like', 'dislike', name='votetype', create_type=False)
    # Lo crea manualmente solo si no existe.
    votetype.create(op.get_bind(), checkfirst=True)

    # Crea la tabla, usando el tipo ya definido sin intentar crearlo de nuevo.
    op.create_table('resource_votes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('resource_link_id', sa.String(length=100), nullable=False),
    sa.Column('vote_type', votetype, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['resource_link_id'], ['resource_links.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'resource_link_id', name='_user_resource_uc')
    )
    op.create_index(op.f('ix_resource_votes_id'), 'resource_votes', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_resource_votes_id'), table_name='resource_votes')
    op.drop_table('resource_votes')
    
    # Define el tipo ENUM y lo borra solo si existe
    votetype = postgresql.ENUM('like', 'dislike', name='votetype', create_type=False)
    votetype.drop(op.get_bind(), checkfirst=True)
