import os
import sys

# Añadir la raíz del proyecto al path para poder importar 'app'
# Esto es necesario para que los siguientes imports funcionen
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from app.db.session import engine
from app.db.base import Base  # Asegura que todos los modelos se cargan
from app.core.config import settings

def reset_database():
    """
    Borra la base de datos existente (si la hay) y crea una nueva
    con el esquema más reciente basado en los modelos.
    """
    db_file = settings.SQLALCHEMY_DATABASE_URI.replace("sqlite+aiosqlite:///", "")
    
    print(f"La base de datos se encuentra en: {db_file}")

    if os.path.exists(db_file):
        print("Borrando base de datos existente...")
        os.remove(db_file)
        print("Base de datos borrada.")

    print("Creando nuevas tablas...")
    # El import de 'Base' ya ha cargado todos los modelos en Base.metadata
    Base.metadata.create_all(bind=engine)
    print("¡Nuevas tablas creadas con éxito!")
    print("La base de datos ha sido reseteada al esquema más reciente.")

if __name__ == "__main__":
    reset_database() 