import asyncio
import argparse
import logging
import os
import re
import sys
from datetime import datetime, timezone, date
from pathlib import Path
from typing import Any, Dict, List, Type

# --- Explicitly load .env file from the correct location ---
from dotenv import load_dotenv
# Goes up three levels (db -> app -> backend) to find .env in the project root
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# --- Adjust path to allow app imports ---
# This makes the script robust and executable from different locations.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# --- All imports grouped here ---
from sqlalchemy import select, func, or_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.core.config import settings
from app.core.security import get_password_hash
from app.db.base import Base
from app.db.models.blog_post import BlogPost
from app.db.models.contact import ContactMessage
from app.db.models.news_item import NewsItem
from app.db.models.project import Project
from app.db.models.resource_link import ResourceLink
from app.db.models.resource_vote import ResourceVote, VoteType
from app.db.models.user import User
from app.db.session import AsyncSessionLocal, SyncSessionLocal
from app.schemas.blog import BlogPostInDBBase
from app.schemas.contact import ContactForm
from app.schemas.news import NewsItemCreate
from app.schemas.project import ProjectRead
from app.schemas.resource_link import ResourceLinkCreate
from app.schemas.user import User as UserSchema, UserCreate

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
}

# Order for dumping to ensure referential integrity if loaded sequentially
DUMP_ORDER: List[str] = ["users", "projects", "blog_posts", "news_items", "resource_links", "resource_votes", "contact_messages"]

# Order for syncing to respect foreign key constraints
SYNC_ORDER: List[str] = ["users", "blog_posts", "projects", "news_items", "resource_links", "resource_votes"]

# Order for cleaning to respect foreign key constraints (reverse of creation)
CLEAN_ORDER: List[str] = list(reversed(SYNC_ORDER))


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


async def fix_blog_post_slugs():
    """Repairs blog posts with null or empty slugs in the database."""
    logger.info("--- [FIX] Starting repair of blog post slugs...")
    db = AsyncSessionLocal()
    try:
        query = select(BlogPost).filter(or_(BlogPost.slug == None, BlogPost.slug == ""))
        result = await db.execute(query)
        posts_to_fix = result.scalars().all()

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

        await db.commit()
        logger.info(f"--- [FIX] Repaired and saved {len(posts_to_fix)} slugs.")

    except Exception as e:
        logger.error(f"--- [FIX] An error occurred during slug repair: {e}", exc_info=True)
        await db.rollback()
    finally:
        await db.close()


def clean_duplicate_news_by_image():
    """Finds and removes duplicate news items based on the imageUrl, keeping the first entry."""
    logger.info("--- [CLEAN] Starting cleanup of duplicate news by imageUrl...")
    db = SyncSessionLocal()
    try:
        subquery = (
            select(NewsItem.imageUrl)
            .group_by(NewsItem.imageUrl)
            .having(func.count(NewsItem.id) > 1)
            .where(NewsItem.imageUrl.isnot(None))
            .alias("duplicated_urls")
        )

        duplicated_urls = db.execute(select(subquery)).scalars().all()

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
            delete_stmt = delete(NewsItem).where(NewsItem.id.in_(ids_to_delete))
            db.execute(delete_stmt)
            db.commit()
            logger.info("--- [CLEAN] Cleanup of duplicate news completed.")
        else:
            logger.info("--- [CLEAN] No duplicates found to delete (data may have changed during operation).")

    except Exception as e:
        logger.error(f"--- [CLEAN] An error occurred during duplicate news cleanup: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


async def dump_data(db: AsyncSession):
    """Dumps all data from the database into a Python file, ensuring data integrity."""
    logger.info("--- [DUMP] Starting database data dump...")
    output_path = Path(__file__).parent / "initial_data.py"
    all_data = {}

    for model_name_plural in DUMP_ORDER:
        Model = get_model_by_name(model_name_plural)
        logger.info(f"--- [DUMP] Dumping data for {model_name_plural}...")
        stmt = select(Model)
        result = await db.execute(stmt)
        items = result.scalars().all()
        item_dicts = [{c.name: getattr(item, c.name) for c in item.__table__.columns} for item in items]
        
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

        for name in DUMP_ORDER:
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


async def get_or_create_superuser(db: "AsyncSession", superuser_data: Dict[str, Any]) -> User:
    """Gets the superuser or creates them if they don't exist."""
    from app import schemas
    from app.core.config import settings

    email = superuser_data.get("email")
    user = await crud.user.get_by_email(db, email=email)
    
    if user:
        logger.info(f"Superuser '{email}' already exists, skipping creation.")
        return user
        
    logger.info(f"Superuser '{email}' not found, creating it...")
    
    # The CRUD create method requires a password. We'll add it from settings.
    user_data_with_password = superuser_data.copy()
    user_data_with_password["password"] = settings.FIRST_SUPERUSER_PASSWORD
    
    # Now we can validate against the standard UserCreate schema
    user_in = schemas.user.UserCreate(**user_data_with_password)
    
    # Use the standard create method
    try:
        created_user = await crud.user.create(db, obj_in=user_in)
        return created_user
    except IntegrityError:
        logger.warning(f"Superuser '{email}' was likely created in a concurrent session. Fetching again.")
        await db.rollback()
        user = await crud.user.get_by_email(db, email=email)
        if not user:
            # This should be a very rare condition.
            logger.error(f"FATAL: Failed to create or retrieve superuser '{email}'.")
            raise
        return user


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


async def sync_model(db: "AsyncSession", model_name: str, data_list: List[Dict[str, Any]]):
    """Generic function to sync data for a single model by adding items that do not exist."""
    logger.info(f"--- [SYNC] Synchronizing data for table: {model_name}...")
    Model = get_model_by_name(model_name)
    
    # Use email as the key for users, otherwise fallback to a more generic key
    if model_name == "users":
        unique_key_name = "email"
        stmt = select(Model.email)
        result = await db.execute(stmt)
        existing_keys = {str(key) for key in result.scalars().all()}
        data_by_key = {str(item['email']): item for item in data_list if 'email' in item}
    elif model_name == "news_items":
        unique_key_name = "url"
        stmt = select(Model.url)
        result = await db.execute(stmt)
        existing_keys = {str(key) for key in result.scalars().all()}
        data_by_key = {str(item['url']): item for item in data_list if 'url' in item}
    elif model_name == "blog_posts":
        unique_key_name = "slug"
        stmt = select(Model.slug)
        result = await db.execute(stmt)
        existing_keys = {str(key) for key in result.scalars().all()}
        data_by_key = {str(item['slug']): item for item in data_list if 'slug' in item}
    else:
        unique_key_name = "id"
        stmt = select(Model.id)
        result = await db.execute(stmt)
        existing_keys = {str(key) for key in result.scalars().all()}
        data_by_key = {str(item['id']): item for item in data_list if 'id' in item}

    logger.info(f"--- [SYNC] Found {len(existing_keys)} existing items in DB for {model_name} using key '{unique_key_name}'.")

    items_to_add = []
    for item_key, item_data in data_by_key.items():
        if item_key not in existing_keys:
            # Special handling for users who might not have a password in initial_data
            if model_name == "users" and 'hashed_password' not in item_data:
                item_data['hashed_password'] = get_password_hash("default_password")
            
            # Ensure created_at is a datetime object if the model has this attribute and it's missing
            if hasattr(Model, 'created_at') and 'created_at' not in item_data:
                # For news_items, 'publishedAt' is the source of truth if 'created_at' is missing
                if model_name == 'news_items' and 'publishedAt' in item_data:
                    item_data['created_at'] = item_data['publishedAt']
                else:
                    item_data['created_at'] = datetime.now(timezone.utc)

            items_to_add.append(Model(**item_data))

    if items_to_add:
        db.add_all(items_to_add)
        logger.info(f"--- [SYNC] Added {len(items_to_add)} new items to '{model_name}' session.")
    else:
        logger.info(f"--- [SYNC] No new items to add for '{model_name}'.")
    try:
        await db.flush()
    except Exception as e:
        logger.error(f"--- [SYNC] Error flushing for {model_name}: {e}")
        raise


async def seed_data(db: "AsyncSession"):
    """Fills the database with initial data from the file."""
    logger.info("--- [SEED] Starting the database seeding process...")
    try:
        from app.db import initial_data
        
        # Ensure the superuser exists and commit it to make its ID available.
        superuser = await get_or_create_superuser(db, initial_data.users[0])
        await db.commit()
        await db.refresh(superuser)
        logger.info(f"--- [SEED] Superuser '{superuser.email}' created/verified with ID: {superuser.id}. Transaction committed.")

        prepare_authored_data(initial_data, superuser.id)
        
        for model_name in SYNC_ORDER:
            # We already handled the user creation/syncing logic with get_or_create_superuser
            if model_name == 'users':
                logger.info("--- [SEED] Skipping 'users' in sync loop as it's handled by get_or_create_superuser.")
                # We need to ensure other users from initial_data are also created if they don't exist
                for user_data in initial_data.users[1:]: # Skip the superuser
                     # A simplified get_or_create logic for other users
                    user = await crud.user.get_by_email(db, email=user_data['email'])
                    if not user:
                        user_data_with_password = user_data.copy()
                        user_data_with_password["password"] = "default_password" # Or some other default
                        user_in = UserCreate(**user_data_with_password)
                        await crud.user.create(db, obj_in=user_in)
                        logger.info(f"--- [SEED] Created additional user: {user_data['email']}")
                await db.commit() # Commit after creating additional users
                continue

            if hasattr(initial_data, model_name):
                data_list = getattr(initial_data, model_name)
                await sync_model(db, model_name, data_list)
                
        await db.commit()
        logger.info("--- [SEED] Database seeding completed successfully.")
    except ImportError:
        logger.error("--- [SEED] initial_data.py not found. Run in 'dump' mode to create it.")
    except Exception as e:
        logger.error(f"--- [SEED] An error occurred during the seeding process: {e}", exc_info=True)
        await db.rollback()


async def clean_database(db: AsyncSession):
    """Deletes all data from the tables in the correct order."""
    logger.info("--- [CLEAN] Starting database cleaning process...")
    for model_name in CLEAN_ORDER:
        try:
            Model = get_model_by_name(model_name)
            stmt = delete(Model)
            await db.execute(stmt)
            logger.info(f"--- [CLEAN] Deleted all records from {model_name}.")
        except ValueError as e:
            logger.warning(f"--- [CLEAN] Could not find model for {model_name}. Skipping. Error: {e}")
        except Exception as e:
            logger.error(f"--- [CLEAN] Error cleaning table {model_name}: {e}", exc_info=True)
            # Depending on the desired behavior, you might want to stop or continue.
            # For a full reset, it's better to raise the exception to halt the process.
            raise
    await db.commit()
    logger.info("--- [CLEAN] Database cleaning finished.")


async def main():
    """Main function to handle script logic."""
    parser = argparse.ArgumentParser(description="Database Seeding and Maintenance Tool")
    parser.add_argument(
        "mode",
        choices=["sync", "dump", "fix-slugs", "clean-news", "reset"],
        help=(
            "'sync': Synchronize the database with initial_data.py. "
            "'dump': Dump data from the database to initial_data.py. "
            "'fix-slugs': Fix blog posts with null slugs. "
            "'clean-news': Remove duplicate news items by imageUrl. "
            "'reset': Clean the database and then synchronize it."
        )
    )
    args = parser.parse_args()

    # --- Direct DB Connection Override for Local Reset ---
    # This bypasses any environment or caching issues for the reset command.
    database_url = os.getenv("DATABASE_URL")
    if args.mode == 'reset' and database_url:
        logger.warning("--- [MAIN] DATABASE_URL detected for 'reset' mode.")
        logger.warning(f"--- [MAIN] Targeting remote database: ...{database_url[-20:]}")
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy.orm import sessionmaker
        
        # Ensure the URL is in the correct async format
        if not database_url.startswith("postgresql+asyncpg"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")

        engine = create_async_engine(database_url)
        AsyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
    else:
        from app.db.session import AsyncSessionLocal

    logger.info("Initializing DB session")
    db = AsyncSessionLocal()

    try:
        if args.clean_duplicates:
            clean_duplicate_news_by_image()
        elif args.fix_slugs:
            await fix_blog_post_slugs()
        elif args.dump:
            await dump_data(db)
        elif args.mode == "reset":
            logger.warning("--- [MAIN] DATABASE_URL detected for 'reset' mode.")
            logger.warning(f"--- [MAIN] Targeting remote database: ...{str(settings.ASYNC_DATABASE_URI)[-20:]}")
            await clean_database(db)
            await seed_data(db)
        else: # 'seed' or no mode specified
            await seed_data(db)
    except Exception as e:
        logger.error(f"--- [MAIN] A critical error occurred: {e}", exc_info=True)
    finally:
        logger.info("DB session closed")
        await db.close()
        # Give a moment for background tasks (like DB connection closing) to complete.
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    if "PROJECT_NAME" not in os.environ:
        os.environ["PROJECT_NAME"] = "ivanintech"
    asyncio.run(main())
