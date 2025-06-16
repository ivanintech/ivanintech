import asyncio
from datetime import datetime
from typing import Dict, Type, List, Any
import logging
import argparse
import os
import sys
from pydantic import BaseModel
from sqlalchemy import select, func

# --- Configuración de logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Ajuste de la ruta para permitir importaciones de la app ---
# Esto asume que el script se ejecuta desde el directorio 'backend'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.db.base import Base
from app.db.models.project import Project
from app.db.models.blog_post import BlogPost
from app.db.models.news_item import NewsItem
from app.db.models.resource_link import ResourceLink
from app.db.models.user import User
from app.db.models.contact import ContactMessage
from app.db.models.resource_vote import ResourceVote, VoteType

from app.schemas.project import ProjectSchema
from app.schemas.blog_post import BlogPostCreate
from app.schemas.news_item import NewsItemCreate
from app.schemas.resource_link import ResourceLinkCreate
from app.schemas.user import User as UserSchema
from app.schemas.contact import ContactForm

# --- Mapa de Modelos a Esquemas Pydantic y Nombres de Datos ---
MODEL_SCHEMA_MAP: Dict[str, Dict[str, Any]] = {
    "User": {"model": User, "schema": UserSchema},
    "Project": {"model": Project, "schema": ProjectSchema},
    "BlogPost": {"model": BlogPost, "schema": BlogPostCreate},
    "NewsItem": {"model": NewsItem, "schema": NewsItemCreate},
    "ResourceLink": {"model": ResourceLink, "schema": ResourceLinkCreate},
    "ContactMessage": {"model": ContactMessage, "schema": ContactForm},
    "ResourceVote": {"model": ResourceVote, "schema": None},  # No hay esquema de lectura explícito
}

DATA_NAMES: List[str] = ["users", "projects", "blog_posts", "news_items", "resource_links", "contact_messages", "resource_votes"]

def dump_data_to_file():
    """Vuelca los datos de la base de datos local a un fichero initial_data.py."""
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", "db", "initial_data.py")
    logging.info(f"--- [DUMP] Iniciando volcado de datos a {output_file} ---")
    
    db = SessionLocal()
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# -*- coding: utf-8 -*-\n")
            f.write("# Este fichero ha sido auto-generado por seed_db.py. No lo edites manualmente.\n")
            f.write("from datetime import datetime\n")
            f.write("from app.db.models.resource_vote import VoteType\n\n")

            for name in DATA_NAMES:
                # Transforma 'resource_links' a 'ResourceLink'
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
                        data = schema.from_orm(item).dict(exclude_unset=True)
                    else:
                        data = {c.name: getattr(item, c.name) for c in item.__table__.columns}

                    if name == "users":
                        data.pop('password', None) # Nunca exportar el password en texto plano
                    
                    if name == "resource_votes":
                        if 'vote_type' in data and isinstance(data['vote_type'], VoteType):
                            data['vote_type'] = f"VoteType.{data['vote_type'].name}"

                    f.write("    {\n")
                    for key, value in data.items():
                        if isinstance(value, datetime):
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

async def seed_data():
    """Rellena la base de datos con los datos iniciales del fichero."""
    logging.info("--- [SEED] Iniciando el proceso de 'seeding' de la base de datos... ---")
    
    try:
        # La importación ahora es relativa a la ubicación del script
        from app.db.initial_data import (
            users, projects, blog_posts, news_items, 
            resource_links, contact_messages, resource_votes
        )
        
        data_map = {
            "User": users,
            "Project": projects,
            "BlogPost": blog_posts,
            "NewsItem": news_items,
            "ResourceLink": resource_links,
            "ContactMessage": contact_messages,
            "ResourceVote": resource_votes,
        }
        
        async with SessionLocal() as db:
            for model_name, data_list in data_map.items():
                model_info = MODEL_SCHEMA_MAP.get(model_name)
                if not model_info:
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
                    if model_name == "ResourceVote" and 'vote_type' in item_data:
                        vote_type_str = item_data['vote_type']
                        if isinstance(vote_type_str, str):
                           member_name = vote_type_str.split('.')[-1]
                           item_data['vote_type'] = VoteType[member_name]
                    
                    db_obj = model(**item_data)
                    db.add(db_obj)
                
                await db.commit()
        logging.info("--- [SEED] Proceso de 'seeding' completado con éxito. ---")

    except ImportError:
        logging.warning("--- [SEED] No se encontró el fichero 'initial_data.py'. Saltando el 'seeding'.")
        logging.warning("--- [SEED] Puedes generar este fichero ejecutando: python seed_db.py --mode dump")
    except Exception as e:
        logging.error(f"--- [SEED] Ocurrió un error: {e}", exc_info=True)
        if 'db' in locals() and db.in_transaction():
            await db.rollback()
            logging.info("--- [SEED] Rollback realizado. ---")

async def main():
    """Función principal para manejar los argumentos de la línea de comandos."""
    parser = argparse.ArgumentParser(description="Script para gestionar la base de datos de la aplicación.")
    parser.add_argument(
        "--mode", 
        type=str, 
        choices=["dump", "seed"], 
        required=True,
        help="'dump' para exportar datos a un fichero, 'seed' para poblar la BD desde el fichero."
    )
    args = parser.parse_args()

    # Creación de la base de datos y tablas si no existen
    # Esto es importante para el primer 'dump' en un entorno limpio
    logging.info("Asegurando que la base de datos y las tablas existen...")
    from app.db.base import engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    if args.mode == "dump":
        dump_data_to_file()
    elif args.mode == "seed":
        await seed_data()

if __name__ == "__main__":
    asyncio.run(main()) 