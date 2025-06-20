"""migracion inicial

Revision ID: a76de84ab972
Revises: 
Create Date: 2025-06-08 23:36:58.894931

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from app.db.models.news_item import GUID


# revision identifiers, used by Alembic.
revision: str = 'a76de84ab972'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('contact_messages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('message', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contact_messages_id'), 'contact_messages', ['id'], unique=False)
    op.create_index(op.f('ix_contact_messages_name'), 'contact_messages', ['name'], unique=False)
    op.create_table('news_items',
    sa.Column('id', GUID(), nullable=False),
    sa.Column('title', sa.String(length=512), nullable=False),
    sa.Column('url', sa.String(length=2048), nullable=False),
    sa.Column('publishedAt', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('imageUrl', sa.String(length=2048), nullable=True),
    sa.Column('relevance_score', sa.Integer(), nullable=True),
    sa.Column('sectors', sa.JSON(), nullable=True),
    sa.Column('sourceName', sa.String(length=255), nullable=True),
    sa.Column('sourceId', sa.String(length=255), nullable=True),
    sa.Column('star_rating', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_news_items_title'), 'news_items', ['title'], unique=False)
    op.create_index(op.f('ix_news_items_url'), 'news_items', ['url'], unique=True)
    op.create_table('projects',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('technologies', sa.JSON(), nullable=False),
    sa.Column('imageUrl', sa.String(length=500), nullable=True),
    sa.Column('videoUrl', sa.String(length=500), nullable=True),
    sa.Column('githubUrl', sa.String(length=500), nullable=True),
    sa.Column('liveUrl', sa.String(length=500), nullable=True),
    sa.Column('is_featured', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)
    op.create_index(op.f('ix_projects_is_featured'), 'projects', ['is_featured'], unique=False)
    op.create_index(op.f('ix_projects_title'), 'projects', ['title'], unique=False)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.Column('full_name', sa.String(length=255), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=False)
    op.create_table('blog_posts',
    sa.Column('id', sa.String(length=100), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('slug', sa.String(length=255), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('excerpt', sa.Text(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.Column('published_date', sa.Date(), nullable=False),
    sa.Column('last_modified_date', sa.Date(), nullable=True),
    sa.Column('tags', sa.String(length=255), nullable=True),
    sa.Column('image_url', sa.String(length=512), nullable=True),
    sa.Column('linkedin_post_url', sa.String(length=512), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_blog_posts_id'), 'blog_posts', ['id'], unique=False)
    op.create_index(op.f('ix_blog_posts_slug'), 'blog_posts', ['slug'], unique=True)
    op.create_index(op.f('ix_blog_posts_status'), 'blog_posts', ['status'], unique=False)
    op.create_index(op.f('ix_blog_posts_title'), 'blog_posts', ['title'], unique=False)
    op.create_table('item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_item_id'), 'item', ['id'], unique=False)
    op.create_index(op.f('ix_item_owner_id'), 'item', ['owner_id'], unique=False)
    op.create_index(op.f('ix_item_title'), 'item', ['title'], unique=False)
    op.create_table('resource_links',
    sa.Column('id', sa.String(length=100), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('url', sa.String(length=2048), nullable=False),
    sa.Column('ai_generated_description', sa.Text(), nullable=True),
    sa.Column('personal_note', sa.Text(), nullable=True),
    sa.Column('resource_type', sa.String(length=50), nullable=True),
    sa.Column('tags', sa.String(length=255), nullable=True),
    sa.Column('thumbnail_url', sa.String(length=2048), nullable=True),
    sa.Column('star_rating', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.Column('is_pinned', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_resource_links_id'), 'resource_links', ['id'], unique=False)
    op.create_index(op.f('ix_resource_links_is_pinned'), 'resource_links', ['is_pinned'], unique=False)
    op.create_index(op.f('ix_resource_links_resource_type'), 'resource_links', ['resource_type'], unique=False)
    op.create_index(op.f('ix_resource_links_tags'), 'resource_links', ['tags'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_resource_links_tags'), table_name='resource_links')
    op.drop_index(op.f('ix_resource_links_resource_type'), table_name='resource_links')
    op.drop_index(op.f('ix_resource_links_is_pinned'), table_name='resource_links')
    op.drop_index(op.f('ix_resource_links_id'), table_name='resource_links')
    op.drop_table('resource_links')
    op.drop_index(op.f('ix_item_title'), table_name='item')
    op.drop_index(op.f('ix_item_owner_id'), table_name='item')
    op.drop_index(op.f('ix_item_id'), table_name='item')
    op.drop_table('item')
    op.drop_index(op.f('ix_blog_posts_title'), table_name='blog_posts')
    op.drop_index(op.f('ix_blog_posts_status'), table_name='blog_posts')
    op.drop_index(op.f('ix_blog_posts_slug'), table_name='blog_posts')
    op.drop_index(op.f('ix_blog_posts_id'), table_name='blog_posts')
    op.drop_table('blog_posts')
    op.drop_index(op.f('ix_user_id'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_projects_title'), table_name='projects')
    op.drop_index(op.f('ix_projects_is_featured'), table_name='projects')
    op.drop_index(op.f('ix_projects_id'), table_name='projects')
    op.drop_table('projects')
    op.drop_index(op.f('ix_news_items_url'), table_name='news_items')
    op.drop_index(op.f('ix_news_items_title'), table_name='news_items')
    op.drop_table('news_items')
    op.drop_index(op.f('ix_contact_messages_name'), table_name='contact_messages')
    op.drop_index(op.f('ix_contact_messages_id'), table_name='contact_messages')
    op.drop_table('contact_messages')
    # ### end Alembic commands ###
