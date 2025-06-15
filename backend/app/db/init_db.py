import logging
from datetime import date # Import date

from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.schemas.user import UserCreate # Import UserCreate
from app.core.config import settings # Import settings
# from app.schemas.project import ProjectCreate # No longer used here
from app.db import initial_data
from app.db.models.project import Project # Import the model
from app.db.models.blog_post import BlogPost # Import BlogPost model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db(db: AsyncSession) -> None:
    """
    Initializes the database with initial data if necessary.
    Uses a single transaction for all initial data.
    """
    logger.info("Starting database initialization with a single transaction...")
    
    try:
        # --- Part 1: Superuser ---
        logger.info("Checking/preparing initial superuser...")
        if settings.FIRST_SUPERUSER:
            user = await crud.user.get_user_by_email(db, email=settings.FIRST_SUPERUSER)
            if not user:
                logger.info(f"Queueing superuser for creation: {settings.FIRST_SUPERUSER}")
                user_in = UserCreate(
                    email=settings.FIRST_SUPERUSER,
                    password=settings.FIRST_SUPERUSER_PASSWORD,
                    full_name="Admin",
                    is_superuser=True,
                    is_active=True,
                )
                # This just adds the user object to the session, no I/O yet
                await crud.user.create_user(db=db, user_in=user_in)
            else:
                logger.info(f"Superuser {settings.FIRST_SUPERUSER} already exists.")
        else:
            logger.warning("FIRST_SUPERUSER not configured. Skipping superuser creation.")

        # --- Part 2: Projects ---
        logger.info("Checking/preparing initial projects...")
        projects_to_add = []
        for project_data in initial_data.initial_projects:
            project_id = project_data.get("id")
            if not project_id:
                logger.warning(f"Project in initial_data without ID, skipping: {project_data.get('title')}")
                continue
            
            existing_project = await db.get(Project, project_id) # More efficient lookup by PK
            
            if not existing_project:
                logger.info(f"Queueing project for creation with ID: {project_id}")
                
                model_data = project_data.copy()
                
                if model_data.get("githubUrl") is not None:
                    model_data["githubUrl"] = str(model_data["githubUrl"])
                if model_data.get("liveUrl") is not None:
                    model_data["liveUrl"] = str(model_data["liveUrl"])
                
                db_project = Project(**model_data) 
                projects_to_add.append(db_project)
        
        if projects_to_add:
            logger.info(f"Adding {len(projects_to_add)} new projects to the session...")
            db.add_all(projects_to_add)
            logger.info(f"{len(projects_to_add)} new projects were queued for creation.")
        else:
            logger.info("No new projects to create.")

        # --- Part 3: Blog Posts ---
        logger.info("Checking/preparing initial blog posts...")
        posts_to_add = []
        for post_data in initial_data.initial_blog_posts:
            post_id = post_data.get("id")
            if not post_id:
                logger.warning(f"Post in initial_data without ID, skipping: {post_data.get('title')}")
                continue
            
            existing_post = await db.get(BlogPost, post_id)
            
            if not existing_post:
                logger.info(f"Queueing post for creation with ID: {post_id}")
                
                model_data = post_data.copy()
                
                if "author_id" not in model_data:
                    model_data["author_id"] = 1 # Relies on the user with ID 1 being created in this transaction
                    logger.info(f"Assigning default author_id=1 to post {post_id}")
                
                try:
                    db_post = BlogPost(**model_data) 
                    posts_to_add.append(db_post)
                except Exception as e:
                    logger.error(f"Error creating BlogPost model instance for ID {post_id}: {e}", exc_info=True)
            
        if posts_to_add:
            logger.info(f"Adding {len(posts_to_add)} new blog posts to the session...")
            db.add_all(posts_to_add)
            logger.info(f"{len(posts_to_add)} new blog posts were queued for creation.")
        else:
            logger.info("No new blog posts to create.")

        # --- Final Commit ---
        logger.info("Committing all queued data to the database...")
        await db.commit()
        logger.info("Initial data committed successfully.")

    except Exception as e:
        logger.error(f"Error during single-transaction database initialization: {e}", exc_info=True)
        await db.rollback()
        raise

    logger.info("Database initialization completed.") 