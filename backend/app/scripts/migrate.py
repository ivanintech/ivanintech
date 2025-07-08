import argparse
import os
import sys
from alembic.config import Config
from alembic import command

# Añadir el directorio raíz al path para que encuentre 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings

def get_sync_db_url(db_uri: str) -> str:
    """Generates a synchronous database URL compatible with various drivers."""
    sync_db_url = db_uri
    if "postgresql+asyncpg" in db_uri:
        sync_db_url = db_uri.replace("postgresql+asyncpg", "postgresql+psycopg")
    elif "sqlite+aiosqlite" in db_uri:
        sync_db_url = db_uri.replace("sqlite+aiosqlite", "sqlite")
    
    # Manejar posibles parámetros de PGBouncer de forma más segura
    if "postgresql" in sync_db_url and "?" in sync_db_url:
        sync_db_url += "&options=--prepare-threshold=0"
    elif "postgresql" in sync_db_url:
        sync_db_url += "?options=--prepare-threshold=0"
        
    return sync_db_url

def main():
    parser = argparse.ArgumentParser(description="Alembic migration helper script.")
    parser.add_argument('action', choices=['revision', 'upgrade', 'downgrade'], help="Alembic command to run.")
    parser.add_argument('-m', '--message', help="Revision message for 'revision' action.", default=None)
    parser.add_argument('--autogenerate', action='store_true', help="Enable autogenerate for 'revision' action.")
    
    args = parser.parse_args()

    # Configurar Alembic
    alembic_ini_path = os.path.join(os.path.dirname(__file__), '..', 'alembic.ini')
    alembic_cfg = Config(alembic_ini_path)
    
    # Asegurarse de que la URL de la base de datos es síncrona
    sync_url = get_sync_db_url(str(settings.SQLALCHEMY_DATABASE_URI))
    alembic_cfg.set_main_option("sqlalchemy.url", sync_url)
    
    print(f"Executing alembic {args.action}...")

    try:
        if args.action == 'revision':
            if not args.message:
                print("ERROR: a message (-m) is required for 'revision'")
                sys.exit(1)
            command.revision(alembic_cfg, message=args.message, autogenerate=args.autogenerate)
            print("Revision created successfully.")
        elif args.action == 'upgrade':
            command.upgrade(alembic_cfg, "head")
            print("Upgrade completed successfully.")
        elif args.action == 'downgrade':
            command.downgrade(alembic_cfg, "base")
            print("Downgrade completed successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 