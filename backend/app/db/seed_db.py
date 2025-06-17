import asyncio
from datetime import datetime, timezone
from typing import Dict, Type, List, Any
import logging
import argparse
import os
import sys
from pydantic import BaseModel, HttpUrl
from sqlalchemy import select, func

# --- Configuración de logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Ajuste de la ruta para permitir importaciones de la app ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SyncSessionLocal, AsyncSessionLocal, sync_engine
from app.db.base import Base
from app.db.models.project import Project
from app.db.models.blog_post import BlogPost
from app.db.models.news_item import NewsItem
from app.db.models.resource_link import ResourceLink
from app.db.models.user import User
from app.db.models.contact import ContactMessage
from app.db.models.resource_vote import ResourceVote, VoteType

from app.schemas.project import ProjectRead
from app.schemas.blog import BlogPostCreate
from app.schemas.news import NewsItemCreate
from app.schemas.resource_link import ResourceLinkCreate
from app.schemas.user import User as UserSchema
from app.schemas.contact import ContactForm

# --- Mapa de Modelos a Esquemas Pydantic y Nombres de Datos ---
MODEL_SCHEMA_MAP: Dict[str, Dict[str, Any]] = {
    "User": {"model": User, "schema": UserSchema},
    "Project": {"model": Project, "schema": ProjectRead},
    "BlogPost": {"model": BlogPost, "schema": BlogPostCreate},
    "NewsItem": {"model": NewsItem, "schema": NewsItemCreate},
    "ResourceLink": {"model": ResourceLink, "schema": ResourceLinkCreate},
    "ContactMessage": {"model": ContactMessage, "schema": ContactForm},
    "ResourceVote": {"model": ResourceVote, "schema": None},  # No hay esquema de lectura explícito
}

DATA_NAMES: List[str] = ["users", "projects", "blog_posts", "news_items", "resource_links", "contact_messages", "resource_votes"]

def clean_orphan_votes():
    """Elimina registros de resource_votes que apuntan a resource_links inexistentes."""
    logging.info("--- [CLEAN] Iniciando limpieza de votos huérfanos...")
    db = SyncSessionLocal()
    try:
        # Usamos una subconsulta para encontrar los IDs de resource_links que no existen
        subquery = select(ResourceVote.resource_link_id).distinct().where(
            ~select(ResourceLink.id).where(ResourceLink.id == ResourceVote.resource_link_id).exists()
        )
        
        # Construimos la consulta de borrado
        delete_stmt = ResourceVote.__table__.delete().where(
            ResourceVote.resource_link_id.in_(subquery)
        )
        
        result = db.execute(delete_stmt)
        deleted_count = result.rowcount
        
        if deleted_count > 0:
            logging.info(f"--- [CLEAN] Se han eliminado {deleted_count} votos huérfanos.")
            db.commit()
        else:
            logging.info("--- [CLEAN] No se encontraron votos huérfanos. La base de datos está limpia.")
            db.rollback()  # No hay cambios que confirmar
            
    except Exception as e:
        logging.error(f"--- [CLEAN] Ocurrió un error durante la limpieza: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()
    logging.info("--- [CLEAN] Proceso de limpieza completado ---")

def dump_data_to_file():
    """Vuelca los datos de la base de datos local a un fichero initial_data.py."""
    # Ruta al directorio actual (donde está seed_db.py, es decir, backend/app/db)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construir la ruta correcta para initial_data.py dentro de este mismo directorio
    output_file = os.path.join(current_dir, "initial_data.py")
    logging.info(f"--- [DUMP] Iniciando volcado de datos a {output_file} ---")
    
    db = SyncSessionLocal()
    try:
        # Asegurarse de que el directorio de destino existe
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# -*- coding: utf-8 -*-\n")
            f.write("# Este fichero ha sido auto-generado por seed_db.py. No lo edites manualmente.\n")
            f.write("from datetime import datetime\n")
            f.write("from app.db.models.resource_vote import VoteType\n\n")

            for name in DATA_NAMES:
                model_name_pascal = "".join([s.capitalize() for s in name.removesuffix('s').replace('_', ' ').split(' ')])
                model_info = MODEL_SCHEMA_MAP.get(model_name_pascal)

                if not model_info:
                    logging.warning(f"No se encontró información del modelo para '{name}'. Saltando...")
                    continue

                model = model_info["model"]
                schema = model_info["schema"]
                
                logging.info(f"--- [DUMP] Leyendo tabla: {model.__tablename__}...")
                items = db.query(model).all()
                logging.info(f"--- [DUMP] Encontrados {len(items)} registros.")
                
                f.write(f"{name} = [\n")
                for item in items:
                    if schema:
                        data = schema.model_validate(item, from_attributes=True).model_dump(exclude_unset=True)
                    else:
                        data = {c.name: getattr(item, c.name) for c in item.__table__.columns}

                    if name == "users":
                        data.pop('password', None)
                    
                    # Ignorar los campos de timestamp para que la BD los genere
                    data.pop('created_at', None)
                    data.pop('updated_at', None)

                    if name == "resource_votes":
                        if 'vote_type' in data and isinstance(data['vote_type'], VoteType):
                            data['vote_type'] = f"VoteType.{data['vote_type'].name}"

                    f.write("    {\n")
                    for key, value in data.items():
                        if isinstance(value, HttpUrl):
                            formatted_value = repr(str(value))
                        elif isinstance(value, datetime):
                            formatted_value = f"datetime.fromisoformat('{value.isoformat()}')"
                        elif isinstance(value, str) and value.startswith("VoteType."):
                             formatted_value = value
                        else:
                            formatted_value = repr(value)
                        
                        f.write(f"        '{key}': {formatted_value},\n")
                    f.write("    },\n")
                f.write("]\n\n")
            
            logging.info(f"--- [DUMP] Escribiendo datos en {os.path.basename(output_file)}...")

    finally:
        db.close()
    logging.info("--- [DUMP] Volcado de datos completado ---")

async def seed_data(db: "AsyncSession"):
    """Rellena la base de datos con los datos iniciales del fichero."""
    logging.info("--- [SEED] Iniciando el proceso de 'seeding' de la base de datos... ---")
    
    try:
        from app.db.initial_data import (
            users, projects, blog_posts, news_items, 
            resource_links, contact_messages, resource_votes
        )
        
        # --- ORDEN DE INSERCIÓN CORRECTO POR DEPENDENCIAS ---
        # 1. Users (no dependencies)
        # 2. Projects, BlogPosts, NewsItems, ResourceLinks (depend on Users)
        # 3. ResourceVotes (depend on Users and ResourceLinks)
        data_map_ordered = {
            "User": users,
            "Project": projects,
            "BlogPost": blog_posts,
            "NewsItem": news_items,
            "ResourceLink": resource_links,
            "ContactMessage": contact_messages,
            "ResourceVote": resource_votes,
        }
        
        for model_name, data_list in data_map_ordered.items():
            model_info = MODEL_SCHEMA_MAP.get(model_name)
            if not model_info:
                logging.warning(f"--- [SEED] No se encontró información de modelo para '{model_name}'. Saltando.")
                continue
            
            model = model_info["model"]
            logging.info(f"--- [SEED] Verificando tabla: {model.__tablename__}...")

            count = (await db.execute(select(func.count()).select_from(model))).scalar()
            if count > 0:
                logging.info(f"--- [SEED] La tabla '{model.__tablename__}' ya contiene {count} registros. Saltando.")
                continue

            if not data_list:
                logging.info(f"--- [SEED] No hay datos iniciales para '{model.__tablename__}'. Saltando.")
                continue

            logging.info(f"--- [SEED] Añadiendo {len(data_list)} registros a la tabla '{model.__tablename__}'...")
            
            for item_data in data_list:
                # --- CONVERSIÓN DE TIPOS Y SANEAMIENTO DE DATOS ---
                clean_data = {}
                for key, value in item_data.items():
                    # Ignorar claves con valor None o timestamps que la BD debe autogenerar
                    if value is None or key in ['updated_at']:
                        continue
                    
                    # Convertir HttpUrl a string
                    if isinstance(value, HttpUrl):
                        clean_data[key] = str(value)
                    # Manejar enums
                    elif model_name == "ResourceVote" and key == 'vote_type' and isinstance(value, str):
                        member_name = value.split('.')[-1]
                        clean_data[key] = VoteType[member_name]
                    else:
                        clean_data[key] = value

                # --- FIX for created_at ---
                if 'created_at' not in clean_data and hasattr(model, 'created_at'):
                    clean_data['created_at'] = datetime.now()
                
                db_obj = model(**clean_data)
                db.add(db_obj)

            try:
                # Usamos flush para persistir los cambios de esta tabla dentro de la misma transacción
                # Esto permite que los IDs generados estén disponibles para las siguientes tablas.
                await db.flush()
                logging.info(f"--- [SEED] 'Flush' completado para la tabla '{model.__tablename__}'.")
            except Exception as e:
                logging.error(f"--- [SEED] Error durante el 'flush' para la tabla '{model.__tablename__}': {e}", exc_info=True)
                await db.rollback() # Revertir toda la transacción si un flush falla
                return # Salir de la función de seed

        # Hacemos commit una sola vez al final si todo ha ido bien
        await db.commit()
        logging.info("--- [SEED] Proceso de 'seeding' completado y transacción confirmada (commit).")

    except ImportError:
        logging.warning("--- [SEED] No se encontró el fichero 'initial_data.py'. Saltando el 'seeding'.")
        logging.warning("--- [SEED] Puedes generar este fichero ejecutando: python seed_db.py --mode dump")
    except Exception as e:
        logging.error(f"--- [SEED] Ocurrió un error general durante el 'seeding': {e}", exc_info=True)
        await db.rollback() # Asegurarse de revertir en caso de error
        raise

async def main():
    """Función principal para manejar los argumentos de la línea de comandos."""
    parser = argparse.ArgumentParser(description="Script para gestionar la base de datos de la aplicación.")
    parser.add_argument(
        "--mode", 
        type=str, 
        choices=["dump", "seed", "clean"], 
        required=True,
        help="'dump' para exportar, 'seed' para poblar, 'clean' para limpiar votos huérfanos."
    )
    args = parser.parse_args()

    # Creación de la base de datos y tablas si no existen
    logging.info("Asegurando que la base de datos y las tablas existen...")
    # Usamos el modo síncrono para crear las tablas para evitar problemas en ciertos entornos
    Base.metadata.create_all(bind=sync_engine)
    logging.info("Comprobación de tablas completada.")
    
    if args.mode == "dump":
        dump_data_to_file()
    elif args.mode == "seed":
        async with AsyncSessionLocal() as db:
            await seed_data(db)
    elif args.mode == "clean":
        clean_orphan_votes()

if __name__ == "__main__":
    asyncio.run(main())