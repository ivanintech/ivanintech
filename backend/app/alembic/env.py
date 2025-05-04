import asyncio
import sys
import os
from logging.config import fileConfig

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# Import Base from your application's model definition
from app.db.base_class import Base 
# Import your models here so Base registers them
from app.db.models.news_item import NewsItem
from app.db.models.project import Project
from app.db.models.blog_post import BlogPost
from app.db.models.user import User
from app.db.models.item import Item 
from app.db.models.contact import ContactMessage 

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Get the database URL from the config
    db_url = config.get_main_option("sqlalchemy.url")
    # Convert async URL to sync URL if needed
    if db_url and db_url.startswith("sqlite+aiosqlite:///" ):
        sync_url = db_url.replace("sqlite+aiosqlite:///", "sqlite:///")
    elif db_url and db_url.startswith("postgresql+asyncpg://"):
        sync_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    else:
        sync_url = db_url

    context.configure(
        url=sync_url,  # Use sync URL for offline mode
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Add render_as_batch for offline SQLite
        render_as_batch=db_url.startswith("sqlite") if db_url else False
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    # Configure context with batch mode enabled for SQLite dialect
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # Add this line to enable batch mode for SQLite
        render_as_batch=connection.dialect.name == "sqlite",
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Create AsyncEngine directly from the ASYNC URL in config
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"), # Get URL from alembic.ini
        poolclass=pool.NullPool
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
