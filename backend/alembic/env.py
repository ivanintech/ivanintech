import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy.pool import NullPool

from alembic import context

# Añadir la raíz del proyecto al path para poder importar 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings
from app.db.base import Base # Asegura que los modelos se cargan
# Importa explícitamente los modelos para asegurarte de que Alembic los vea
from app.db.models import User, ResourceLink, BlogPost, NewsItem, Item, ContactMessage, Project, ResourceVote

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Construir la URL de la base de datos síncrona para Alembic
sync_db_url = settings.SQLALCHEMY_DATABASE_URI
if "postgresql+asyncpg" in sync_db_url:
    sync_db_url = sync_db_url.replace("postgresql+asyncpg", "postgresql+psycopg")
elif "sqlite+aiosqlite" in sync_db_url:
    sync_db_url = sync_db_url.replace("sqlite+aiosqlite", "sqlite")

config.set_main_option("sqlalchemy.url", sync_db_url)


# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
