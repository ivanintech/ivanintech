import argparse
import logging
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Type

from dotenv import load_dotenv
import sqlalchemy as sa
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command

# --- Configuration ---
# Goes up three levels (scripts -> app -> backend) to find .env in the project root
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.base import Base
from app.db.models.blog_post import BlogPost
from app.db.models.contact import ContactMessage
from app.db.models.hero_media import HeroMedia
from app.db.models.about_media import AboutMedia
from app.db.models.news_item import NewsItem
from app.db.models.project import Project
from app.db.models.resource_link import ResourceLink
from app.db.models.resource_vote import ResourceVote, VoteType
from app.db.models.user import User
from app.schemas.blog import BlogPostInDBBase
from app.schemas.contact import ContactForm
from app.schemas.news import NewsItemCreate
from app.schemas.project import ProjectRead
from app.schemas.resource_link import ResourceLinkCreate
from app.schemas.hero_media import HeroMedia as HeroMediaSchema
from app.schemas.about_media import AboutMedia as AboutMediaSchema
from app.schemas.user import User as UserSchema, UserCreate

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Database Engine Setup ---
# Use the synchronous engine for reliability in scripting
if not settings.SQLALCHEMY_DATABASE_URI:
    raise RuntimeError("DATABASE_URL must be set in the environment.")

# Ensure we are using a synchronous driver
sync_db_uri = settings.SQLALCHEMY_DATABASE_URI.replace("+asyncpg", "")
engine = create_engine(sync_db_uri)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Model and Schema Mapping ---
# The key is the plural name used in data files.
MODEL_MAP: Dict[str, Dict[str, Any]] = {
    "users": {"model": User, "schema": UserSchema},
    "projects": {"model": Project, "schema": ProjectRead},
    "blog_posts": {"model": BlogPost, "schema": BlogPostInDBBase},
    "news_items": {"model": NewsItem, "schema": NewsItemCreate},
    "resource_links": {"model": ResourceLink, "schema": ResourceLinkCreate},
    "contact_messages": {"model": ContactMessage, "schema": ContactForm},
    "resource_votes": {"model": ResourceVote, "schema": None},  # No explicit read schema
    "hero_media": {"model": HeroMedia, "schema": HeroMediaSchema},
    "about_media": {"model": AboutMedia, "schema": AboutMediaSchema},
}

# This defines the order in which tables should be dropped to respect foreign key constraints.
# Parent tables (like 'user') should be dropped after child tables.
CLEAN_ORDER = [
    "alembic_version",
    "resource_votes",
    "contact_messages",
    "about_media",
    "hero_media",
    "resource_links",
    "news_items",
    "projects",
    "blog_posts",
    "user",
]


def get_model_by_name(model_name_plural: str) -> Type[Base]:
    """Gets a model class by its plural snake_case name."""
    model_info = MODEL_MAP.get(model_name_plural)
    if not model_info:
        raise ValueError(f"Model not found for name: {model_name_plural}")
    return model_info["model"]


def generate_slug(title: str) -> str:
    """Generates a URL-friendly slug from a title."""
    if not title:
        return ""
    s = title.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_-]+', '-', s)
    s = re.sub(r'^-+|-+$', '', s)
    return s


def fix_blog_post_slugs(db: sa.orm.Session):
    """Repairs blog posts with null or empty slugs in the database."""
    logger.info("--- [FIX] Starting repair of blog post slugs...")
    try:
        query = sa.select(BlogPost).filter(sa.or_(BlogPost.slug == None, BlogPost.slug == ""))
        posts_to_fix = db.execute(query).scalars().all()

        if not posts_to_fix:
            logger.info("--- [FIX] No blog posts with null or empty slugs found. No repair needed.")
            return

        logger.info(f"--- [FIX] Found {len(posts_to_fix)} posts to repair.")

        for post in posts_to_fix:
            if post.title:
                new_slug = generate_slug(post.title)
                logger.info(f"--- [FIX] Generating slug for post '{post.title[:30]}...': '{new_slug}'")
                post.slug = new_slug
            else:
                logger.warning(f"--- [FIX] Post with ID {post.id} has no title. Cannot generate slug.")

        db.commit()
        logger.info(f"--- [FIX] Repaired and saved {len(posts_to_fix)} slugs.")

    except Exception as e:
        logger.error(f"--- [FIX] An error occurred during slug repair: {e}", exc_info=True)
        db.rollback()


def clean_duplicate_news_by_image(db: sa.orm.Session):
    """Finds and removes duplicate news items based on the imageUrl, keeping the first entry."""
    logger.info("--- [CLEAN] Starting cleanup of duplicate news by imageUrl...")
    try:
        subquery = (
            sa.select(NewsItem.imageUrl)
            .group_by(NewsItem.imageUrl)
            .having(sa.func.count(NewsItem.id) > 1)
            .where(NewsItem.imageUrl.isnot(None))
            .alias("duplicated_urls")
        )

        duplicated_urls = db.execute(sa.select(subquery)).scalars().all()

        if not duplicated_urls:
            logger.info("--- [CLEAN] No news items with duplicate imageUrls found.")
            return

        logger.info(f"--- [CLEAN] Found {len(duplicated_urls)} duplicate imageUrls. Proceeding to clean...")

        ids_to_delete = []
        for url in duplicated_urls:
            items = db.query(NewsItem.id).filter(NewsItem.imageUrl == url).order_by(NewsItem.id).all()
            ids_to_delete.extend([item.id for item in items[1:]])

        if ids_to_delete:
            logger.info(f"--- [CLEAN] Deleting {len(ids_to_delete)} duplicate news items.")
            delete_stmt = sa.delete(NewsItem).where(NewsItem.id.in_(ids_to_delete))
            db.execute(delete_stmt)
            db.commit()
            logger.info("--- [CLEAN] Cleanup of duplicate news completed.")
        else:
            logger.info("--- [CLEAN] No duplicates found to delete (data may have changed during operation).")

    except Exception as e:
        logger.error(f"--- [CLEAN] An error occurred during duplicate news cleanup: {e}", exc_info=True)
        db.rollback()


def dump_data(db: sa.orm.Session):
    """Dumps all data from the database into a Python file, ensuring data integrity."""
    logger.info("--- [DUMP] Starting database data dump...")
    output_path = Path(__file__).parent.parent / "db" / "initial_data.py"
    all_data = {}
    inspector = sa.inspect(db.bind)

    for model_name_plural in MODEL_MAP.keys():
        Model = get_model_by_name(model_name_plural)
        table_name = Model.__tablename__

        if not inspector.has_table(table_name):
            logger.warning(f"--- [DUMP-WARN] Table '{table_name}' not found. Skipping.")
            continue

        logger.info(f"--- [DUMP] Dumping data for {model_name_plural}...")
        db_columns = inspector.get_columns(table_name)
        db_column_names = {col['name'] for col in db_columns}

        model_columns_to_select = [
            getattr(Model, col_name) 
            for col_name in db_column_names 
            if hasattr(Model, col_name) and isinstance(getattr(Model, col_name), sa.orm.attributes.InstrumentedAttribute)
        ]
        
        stmt = sa.select(*model_columns_to_select)
        result = db.execute(stmt)
        item_dicts = [dict(row._mapping) for row in result.fetchall()]
        
        if item_dicts:
            all_data[model_name_plural] = item_dicts
            logger.info(f"--- [DUMP] Found {len(all_data[model_name_plural])} items for {model_name_plural} to be written.")

    # Integrity Check for resource_votes before writing
    logger.info("--- [DUMP] Performing data integrity checks...")
    if 'resource_links' in all_data and 'resource_votes' in all_data:
        resource_link_ids = {str(rl['id']) for rl in all_data['resource_links']}
        valid_votes, invalid_votes = [], []
        for vote in all_data['resource_votes']:
            if str(vote.get('resource_link_id')) in resource_link_ids:
                valid_votes.append(vote)
            else:
                invalid_votes.append(vote)
        if invalid_votes:
            all_data['resource_votes'] = valid_votes
            logger.warning(f"--- [DUMP] Removed {len(invalid_votes)} orphan resource_votes.")

    logger.info(f"--- [DUMP] Writing data to {output_path}...")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# -*- coding: utf-8 -*-\n")
        f.write("# This file is auto-generated by the seed_db.py script. Do not edit it manually.\n")
        f.write("from datetime import datetime, date, timezone\n")
        f.write("from uuid import UUID\n")
        f.write("from app.db.models.resource_vote import VoteType\n\n")

        for name in MODEL_MAP.keys():
            f.write(f"{name} = [\n")
            for item_dict in all_data.get(name, []):
                item_dict.pop('created_at', None)
                item_dict.pop('updated_at', None)
                if name == "users":
                    item_dict.pop('hashed_password', None)
                f.write("    {\n")
                for key, value in item_dict.items():
                    if isinstance(value, (datetime, date)):
                        if isinstance(value, datetime) and value.tzinfo is None:
                            value = value.astimezone()
                        f.write(f"        '{key}': datetime.fromisoformat('{value.isoformat()}'),\n")
                    elif isinstance(value, VoteType):
                        f.write(f"        '{key}': VoteType.{value.name},\n")
                    else:
                        # Let repr() handle all other types correctly, including str, int, bool, etc.
                        # This is robust for multi-line strings and quotes within strings.
                        f.write(f"        '{key}': {repr(value)},\n")
                f.write("    },\n")
            f.write("]\n\n")
    logger.info(f"--- [DUMP] Data dump completed successfully.")


def get_or_create_user(db: sa.orm.Session, user_data: Dict[str, Any], is_superuser: bool = False) -> User:
    """Gets a user or creates them if they don't exist."""
    from app.core.config import settings

    email = user_data.get("email")
    
    # Use raw SQL to avoid potential ORM issues with pgbouncer.
    # The table is "users", not "user".
    stmt = text('SELECT * FROM "users" WHERE email = :email')
    result = db.execute(stmt, {"email": email}).first()
    
    if result:
        logger.info(f"User '{email}' already exists, skipping creation.")
        # We need to map the raw result back to an ORM object carefully.
        # The database column is 'avatar_url' but the model attribute is 'avatar_path'.
        # The 'avatar_url' on the model is a read-only @property.
        user_data_from_db = dict(result._mapping)
        user_data_for_model = user_data_from_db.copy()

        # Rename key to match the model's attribute
        if 'avatar_url' in user_data_for_model:
            user_data_for_model['avatar_path'] = user_data_for_model.pop('avatar_url')
        
        # Create user object from the corrected data
        user = User(**user_data_for_model)
        return user
        
    logger.info(f"User '{email}' not found, creating it...")
    
    user_data_with_password = user_data.copy()
    
    # Use the superuser password from settings, otherwise a default
    if is_superuser:
        user_data_with_password["password"] = settings.FIRST_SUPERUSER_PASSWORD
    else:
        user_data_with_password["password"] = "default_password"
        
    # Ensure superuser flag is set correctly
    user_data_with_password["is_superuser"] = is_superuser
    
    user_in = UserCreate(**user_data_with_password)
    
    # Manually create the user object
    hashed_password = get_password_hash(user_in.password)
    user_obj = User(
        **user_in.model_dump(exclude={"password"}),
        hashed_password=hashed_password
    )
    
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj


def prepare_authored_data(initial_data, author_id: int):
    """Assigns an author_id/user_id to data before insertion."""
    for post in getattr(initial_data, 'blog_posts', []):
        # Unconditionally set the author_id to the one from the created/verified superuser.
        post['author_id'] = author_id
        if 'published_date' not in post or post['published_date'] is None:
            post['published_date'] = datetime.now(timezone.utc)

    for link in getattr(initial_data, 'resource_links', []):
        # Do the same for resource_links
        link['author_id'] = author_id

    for vote in getattr(initial_data, 'resource_votes', []):
        # Do the same for resource_votes, which uses 'user_id'
        vote['user_id'] = author_id


def sync_model(db: sa.orm.Session, model_name: str, data_list: List[Dict[str, Any]]):
    """
    Generic function to sync a model's data. It commits record by record
    to avoid issues with bulk inserts and server-side defaults.
    """
    if not data_list:
        return
        
    Model = get_model_by_name(model_name)
    logger.info(f"--- [SYNC] Syncing {len(data_list)} items for {model_name} (one by one)...")
    
    for item_data in data_list:
        clean_item_data = {k: v for k, v in item_data.items() if k not in ('created_at', 'updated_at')}
        db_obj = Model(**clean_item_data)
        db.add(db_obj)
        try:
            db.commit()
        except Exception as e:
            logger.error(f"--- [SYNC-ERROR] Could not commit item for {model_name}: {item_data}. Error: {e}")
            db.rollback()
    
    logger.info(f"--- [SYNC] Finished syncing items for {model_name}.")


def seed_data(db: sa.orm.Session):
    """Fills the database with initial data from the file."""
    logger.info("--- [SEED] Starting the database seeding process...")
    try:
        from app.db import initial_data
        
        # 1. Create all users first and commit
        logger.info("--- [SEED] Creating users...")
        superuser_data = initial_data.users[0]
        superuser = get_or_create_user(db, superuser_data, is_superuser=True)
        
        for user_data in initial_data.users[1:]:
            get_or_create_user(db, user_data, is_superuser=False)
        
        logger.info(f"--- [SEED] Superuser '{superuser.email}' created/verified with ID: {superuser.id}.")

        # 2. Prepare data that needs an author ID
        prepare_authored_data(initial_data, superuser.id)
        
        # 3. Sync all other models
        for model_name in MODEL_MAP.keys():
            if model_name == 'users':
                continue
            if hasattr(initial_data, model_name):
                data_list = getattr(initial_data, model_name)
                sync_model(db, model_name, data_list)
                
        logger.info("--- [SEED] Database seeding completed successfully.")
    except ImportError:
        logger.error("--- [SEED] initial_data.py not found. Run in 'dump' mode to create it.")
    except Exception as e:
        logger.error(f"--- [SEED] An error occurred during the seeding process: {e}", exc_info=True)
        db.rollback()


def clean_database(db: sa.orm.Session):
    """Drops all known tables from the database in a specific order."""
    logger.info("--- [CLEAN] Starting database cleaning process...")
    
    # First, try to drop the alembic_version table with raw SQL, as it has no model.
    try:
        logger.info("--- [CLEAN] Dropping alembic_version table with raw SQL...")
        db.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE;"))
        db.commit()
        logger.info("--- [CLEAN] Dropped alembic_version table successfully.")
    except Exception as e:
        logger.error(f"--- [CLEAN] Error dropping alembic_version: {e}")
        db.rollback()

    # Get all table models from the 'models' module
    all_models = [
        m for m in Base.metadata.tables.values()
    ]
    
    logger.info(f"--- [CLEAN] Preparing to drop {len(all_models)} tables with CASCADE...")

    for model_class in all_models:
        table_name = model_class.name
        logger.info(f"--- [CLEAN] Dropping table '{table_name}'...")
        try:
            # Use CASCADE to ensure dependent objects are also dropped
            db.execute(text(f'DROP TABLE IF EXISTS "{table_name}" CASCADE;'))
            db.commit()
            logger.info(f"--- [CLEAN] Dropped table '{table_name}' successfully.")
        except Exception as e:
            logger.error(f"--- [CLEAN] Could not drop table '{table_name}': {e}")
            db.rollback()
            
    logger.info("--- [CLEAN] Database cleaning process finished.")


def main():
    """Main function to orchestrate the database seeding operations."""
    parser = argparse.ArgumentParser(description="Database Seeding and Maintenance Tool")
    parser.add_argument(
        "mode",
        nargs='?',
        default='seed',
        choices=['seed', 'reset', 'dump', 'fix-slugs', 'clean-duplicates', 'test-connection'],
        help="The operation to perform."
    )
    args = parser.parse_args()
    
    logger.info(f"--- [MAIN] Script started with mode: {args.mode}")

    if args.mode == 'test-connection':
        logger.info("--- [TEST] Attempting to connect to the database...")
        db = None
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            logger.info("--- [TEST] Database connection successful!")
            return
        except Exception as e:
            logger.error(f"--- [TEST] Database connection failed: {e}")
            return
        finally:
            if db:
                db.close()

    db = SessionLocal()
    try:
        if args.mode == "reset":
            clean_database(db)
            logger.info("--- [RESET] Database cleaning finished.")

            logger.info("--- [RESET] Running 'alembic upgrade head' to recreate schema...")
            try:
                # Build an absolute, normalized path to the alembic.ini file
                script_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.normpath(os.path.join(script_dir, '..', '..', '..'))
                
                # The alembic.ini file is inside the 'backend' directory
                alembic_ini_path = os.path.join(project_root, 'backend', 'alembic.ini')
                alembic_script_location = os.path.join(project_root, 'backend', 'alembic')
                
                alembic_cfg = Config(alembic_ini_path)
                alembic_cfg.set_main_option("script_location", alembic_script_location)
                
                command.upgrade(alembic_cfg, "head")
                logger.info("--- [RESET] Alembic migrations applied successfully.")
            except Exception as e:
                logger.error(f"--- [RESET-ERROR] Could not apply Alembic migrations: {e}")

        elif args.mode == "seed":
            seed_data(db)

        elif args.mode == "dump":
            dump_data(db)

        elif args.mode == "fix-slugs":
            fix_blog_post_slugs(db)

        elif args.mode == "clean-duplicates":
            clean_duplicate_news_by_image(db)

        else:
            logger.error(f"--- [MAIN] Unknown mode: {args.mode}. Use 'reset', 'seed', or 'dump'.")

    except Exception as e:
        logger.error(f"--- [MAIN] A critical error occurred: {e}", exc_info=True)
        db.rollback()
    finally:
        logger.info("DB session closed")
        db.close()


if __name__ == "__main__":
    if "PROJECT_NAME" not in os.environ:
        os.environ["PROJECT_NAME"] = "ivanintech"
    main()
