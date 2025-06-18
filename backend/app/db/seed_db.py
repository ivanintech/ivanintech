import asyncio
from datetime import datetime, timezone, date
from typing import Dict, Type, List, Any
import logging
import argparse
import os
import sys
import re
from pydantic import BaseModel, HttpUrl

# --- Ajuste de la ruta para permitir importaciones de la app ---
# Esto hace que el script sea robusto y se pueda ejecutar desde distintas ubicaciones.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from sqlalchemy import select, func, or_, delete

# --- Configuración de logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
from app.schemas.blog import BlogPostCreate, BlogPostInDBBase
from app.schemas.news import NewsItemCreate
from app.schemas.resource_link import ResourceLinkCreate
from app.schemas.user import User as UserSchema
from app.schemas.contact import ContactForm

# --- Mapa de Modelos a Esquemas Pydantic y Nombres de Datos ---
MODEL_SCHEMA_MAP: Dict[str, Dict[str, Any]] = {
    "User": {"model": User, "schema": UserSchema},
    "Project": {"model": Project, "schema": ProjectRead},
    "BlogPost": {"model": BlogPost, "schema": BlogPostInDBBase},
    "NewsItem": {"model": NewsItem, "schema": NewsItemCreate},
    "ResourceLink": {"model": ResourceLink, "schema": ResourceLinkCreate},
    "ContactMessage": {"model": ContactMessage, "schema": ContactForm},
    "ResourceVote": {"model": ResourceVote, "schema": None},  # No hay esquema de lectura explícito
}

DATA_NAMES: List[str] = ["users", "projects", "blog_posts", "news_items", "resource_links", "contact_messages", "resource_votes"]

def generate_slug(title: str) -> str:
    if not title:
        return ""
    s = title.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_-]+', '-', s)
    s = re.sub(r'^-+|-+$', '', s)
    return s

async def fix_blog_post_slugs():
    """Repara los slugs de los blog posts que son nulos en la base de datos."""
    logging.info("--- [FIX] Iniciando reparación de slugs de blog posts...")
    db = AsyncSessionLocal()
    try:
        query = select(BlogPost).filter(or_(BlogPost.slug == None, BlogPost.slug == ""))
        result = await db.execute(query)
        posts_to_fix = result.scalars().all()
        
        if not posts_to_fix:
            logging.info("--- [FIX] No se encontraron blog posts con slugs nulos o vacíos. No se necesita reparación.")
            return

        logging.info(f"--- [FIX] Se encontraron {len(posts_to_fix)} posts para reparar.")
        
        for post in posts_to_fix:
            if post.title:
                new_slug = generate_slug(post.title)
                logging.info(f"--- [FIX] Generando slug para el post '{post.title[:30]}...': '{new_slug}'")
                post.slug = new_slug
            else:
                logging.warning(f"--- [FIX] El post con ID {post.id} no tiene título. No se puede generar slug.")

        await db.commit()
        logging.info(f"--- [FIX] Se han reparado y guardado {len(posts_to_fix)} slugs.")

    except Exception as e:
        logging.error(f"--- [FIX] Ocurrió un error durante la reparación de slugs: {e}", exc_info=True)
        await db.rollback()
    finally:
        await db.close()

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

def clean_duplicate_news_by_image():
    """Finds and removes duplicate news items based on the imageUrl, keeping the first entry."""
    logging.info("--- [CLEAN] Iniciando limpieza de noticias duplicadas por imageUrl...")
    db = SyncSessionLocal()
    try:
        # Subquery to find imageUrls that are duplicated
        subquery = (
            select(NewsItem.imageUrl)
            .group_by(NewsItem.imageUrl)
            .having(func.count(NewsItem.id) > 1)
            .where(NewsItem.imageUrl.isnot(None))
            .alias("duplicated_urls")
        )
        
        duplicated_urls = db.execute(select(subquery)).scalars().all()
        
        if not duplicated_urls:
            logging.info("--- [CLEAN] No se encontraron noticias con imageUrls duplicadas.")
            return

        logging.info(f"--- [CLEAN] Se encontraron {len(duplicated_urls)} imageUrls duplicadas. Procediendo a limpiar...")
        
        ids_to_delete = []
        for url in duplicated_urls:
            # For each duplicated URL, get all items ordered by ID (oldest first)
            items = db.query(NewsItem.id).filter(NewsItem.imageUrl == url).order_by(NewsItem.id).all()
            # Add all but the first one (the one to keep) to the deletion list
            ids_to_delete.extend([item.id for item in items[1:]])
            
        if ids_to_delete:
            logging.info(f"--- [CLEAN] Se eliminarán {len(ids_to_delete)} noticias duplicadas.")
            
            delete_stmt = delete(NewsItem).where(NewsItem.id.in_(ids_to_delete))
            db.execute(delete_stmt)
            db.commit()
            
            logging.info("--- [CLEAN] Limpieza de noticias duplicadas completada.")
        else:
            logging.info("--- [CLEAN] No se encontraron duplicados para eliminar (esto puede ocurrir si los datos cambiaron durante la operación).")

    except Exception as e:
        logging.error(f"--- [CLEAN] Ocurrió un error durante la limpieza de noticias duplicadas: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()

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
            f.write("from datetime import datetime, date\n")
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
                        # Check for date objects FIRST, ensuring they are not also datetime objects
                        elif isinstance(value, date) and not isinstance(value, datetime):
                            formatted_value = f"date({value.year}, {value.month}, {value.day})"
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
    """Fills the database with initial data from the file."""
    logging.info("--- [SEED] Starting the database seeding process... ---")
    
    try:
        from app.db import initial_data
        
        # --- 1. Get or create the superuser ---
        superuser = await get_or_create_superuser(db, initial_data.users[0])
        superuser_id = superuser.id
        
        # --- 2. Prepare data with author_id and default dates ---
        prepare_authored_data(initial_data, superuser_id)

        # --- 3. Define insertion order by dependencies ---
        data_map_ordered = {
            "User": initial_data.users,
            "Project": initial_data.projects,
            "BlogPost": initial_data.blog_posts,
            "NewsItem": initial_data.news_items,
            "ResourceLink": initial_data.resource_links,
            "ContactMessage": initial_data.contact_messages,
            "ResourceVote": initial_data.resource_votes,
        }

        # --- 4. Sync each model ---
        for model_name, data_list in data_map_ordered.items():
            await sync_model(db, model_name, data_list)
        
        await db.commit()
        logging.info("--- [SEED] Seeding process completed and transaction committed. ---")

    except ImportError:
        logging.warning("--- [SEED] 'initial_data.py' file not found. Skipping seeding.")
        logging.warning("--- [SEED] You can generate this file by running: python seed_db.py --mode dump")
    except Exception as e:
        logging.error(f"--- [SEED] An error occurred during the seeding process: {e}", exc_info=True)
        await db.rollback()
    finally:
        if db:
            await db.close()
            logging.info("--- [SEED] Database connection closed.")

async def get_or_create_superuser(db: "AsyncSession", superuser_data: Dict[str, Any]) -> User:
    """Gets the superuser or creates them if they don't exist."""
    from app import crud
    email = superuser_data['email']
    user = await crud.user.get_by_email(db, email=email)
    if user:
        logging.info(f"Found existing superuser: {user.email} (ID: {user.id})")
        return user
    
    logging.info(f"Superuser with email {email} not found. Creating a new one...")
    # The password should be present in initial_data, but we have a fallback just in case.
    if 'password' not in superuser_data:
        superuser_data['password'] = "supersecret"
    new_user = await crud.user.create(db, obj_in=superuser_data)
    logging.info(f"Superuser {new_user.email} created with ID: {new_user.id}")
    return new_user

def prepare_authored_data(initial_data, author_id: int):
    """Injects author_id and default dates into relevant data lists."""
    for post in initial_data.blog_posts:
        post['author_id'] = author_id
        if 'published_date' not in post or post['published_date'] is None:
            post['published_date'] = datetime.now(timezone.utc)
    
    for resource in initial_data.resource_links:
        resource['author_id'] = author_id

async def sync_model(db: "AsyncSession", model_name: str, data_list: List[Dict[str, Any]]):
    """Generic function to sync data for a single model."""
    model_info = MODEL_SCHEMA_MAP.get(model_name)
    if not model_info or not data_list:
        return

    model = model_info["model"]
    logging.info(f"--- [SYNC] Synchronizing data for table: {model.__tablename__}...")

    # --- Pre-process data and determine what to insert ---
    items_to_process = []
    primary_keys = [key.name for key in model.__table__.primary_key.columns]

    if len(primary_keys) == 1 and primary_keys[0] == 'id':
        existing_ids_query = await db.execute(select(model.id))
        existing_ids = {str(row[0]) for row in existing_ids_query}  # Cast to str for safety (UUIDs)

        if model_name == "BlogPost":
            existing_slugs_query = await db.execute(select(model.slug).where(model.slug.isnot(None)))
            existing_slugs = {row[0] for row in existing_slugs_query}
            
            for data in data_list:
                slug = data.get("slug") or generate_slug(data.get("title", ""))
                if str(data.get("id")) not in existing_ids and slug not in existing_slugs:
                    data["slug"] = slug
                    items_to_process.append(data)

        elif model_name == "NewsItem":
            existing_urls_query = await db.execute(select(model.url).where(model.url.isnot(None)))
            existing_urls = {row[0] for row in existing_urls_query}

            for data in data_list:
                item_id = str(data.get("id"))
                item_url = data.get("url")
                if item_id not in existing_ids and item_url not in existing_urls:
                    items_to_process.append(data)
        else:
            items_to_process = [d for d in data_list if str(d.get("id")) not in existing_ids]
            
        if not items_to_process:
            logging.info(f"--- [SYNC] All {len(data_list)} items for '{model.__tablename__}' already exist. Skipping.")
            return
    else:  # For composite keys or other cases, insert only if table is empty
        count_query = await db.execute(select(func.count()).select_from(model))
        if count_query.scalar_one() > 0:
            logging.info(f"--- [SYNC] Table '{model.__tablename__}' is not empty ({count_query.scalar_one()} items). Skipping.")
            return
        items_to_process = data_list

    # --- Data Sanitization & Object Creation ---
    objects_to_add = []
    for data in items_to_process:
        # Final check for slug to prevent critical errors
        if model_name == "BlogPost" and not data.get("slug"):
            logging.error(f"--- [SYNC] CRITICAL: Attempted to add blog post '{data.get('title')}' without a slug. Skipping entry.")
            continue
        
        # Convert enums from string representation to Enum members
        if model_name == "ResourceVote" and 'vote_type' in data and isinstance(data['vote_type'], str):
            data['vote_type'] = VoteType[data['vote_type'].split('.')[-1]]

        objects_to_add.append(model(**data))
        
    if not objects_to_add:
        logging.info(f"--- [SYNC] No new items to add to '{model.__tablename__}' after all checks.")
        return

    db.add_all(objects_to_add)
    logging.info(f"--- [SYNC] Added {len(objects_to_add)} new items to '{model.__tablename__}' session.")
    await db.flush()  # Flush to ensure IDs are available for subsequent operations

async def main():
    """Función principal para manejar la lógica del script."""
    parser = argparse.ArgumentParser(description="Script para gestionar la base de datos de la aplicación.")
    parser.add_argument(
        "--mode",
        choices=["seed", "dump", "fix-slugs", "clean-news-duplicates"],
        required=True,
        help="El modo de operación: 'seed' para poblar la BD, 'dump' para volcar datos, 'fix-slugs' para reparar slugs nulos, 'clean-news-duplicates' para eliminar noticias duplicadas."
    )
    args = parser.parse_args()

    if args.mode == "seed":
        # El seeder ya es asíncrono, así que lo llamamos directamente
        db = AsyncSessionLocal()
        await seed_data(db)
    elif args.mode == "dump":
        dump_data_to_file()
    elif args.mode == "fix-slugs":
        await fix_blog_post_slugs()
    elif args.mode == "clean-news-duplicates":
        clean_duplicate_news_by_image()

if __name__ == "__main__":
    # Ajustar la ruta para permitir importaciones directas de la app
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    asyncio.run(main())