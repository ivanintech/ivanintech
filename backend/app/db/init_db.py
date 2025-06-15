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
    Checks if projects and posts already exist before inserting them.
    """
    logger.info("Starting database initialization...")
    
    # --- Create Superuser if it doesn't exist ---
    logger.info("Checking/creating initial superuser...")
    if not settings.FIRST_SUPERUSER:
        logger.warning(
            "FIRST_SUPERUSER is not configured in environment variables. "
            "Skipping superuser creation."
        )
    else:
        user = await crud.user.get_user_by_email(db, email=settings.FIRST_SUPERUSER)
        if not user:
            logger.info(f"Creating superuser: {settings.FIRST_SUPERUSER}")
            user_in = UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                full_name="Admin", # You can change this or make it configurable
                is_superuser=True,
                is_active=True, # Superuser should be active by default
            )
            try:
                await crud.user.create_user(db=db, user_in=user_in)
                await db.commit() # Commit the user so it gets an ID
                logger.info("Superuser created successfully.")
            except Exception as e:
                logger.error(f"Error creating superuser: {e}", exc_info=True)
                # Consider whether to rollback or re-raise the exception here
                # depending on whether superuser creation is critical for startup
                await db.rollback() # Rollback this creation attempt
                # raise # You could re-raise if it's critical for the superuser to exist
        else:
            logger.info(f"Superuser {settings.FIRST_SUPERUSER} already exists.")
    
    # --- Populate Projects ---
    logger.info("Checking/populating initial projects...")
    projects_created_count = 0
    projects_to_add = [] # List to add in batch
    
    for project_data in initial_data.initial_projects:
        project_id = project_data.get("id")
        if not project_id:
            logger.warning(f"Project in initial_data without ID, skipping: {project_data.get('title')}")
            continue
            
        existing_project = await crud.portfolio.get_project(db, project_id=project_id)
        
        if not existing_project:
            logger.info(f"Preparing to create project with ID: {project_id}")
            
            # --- Create MODEL instance directly --- #
            # Copy the dictionary to avoid modifying the original
            model_data = project_data.copy()
            
            # Convert HttpUrl to string if they exist
            if model_data.get("githubUrl") is not None:
                model_data["githubUrl"] = str(model_data["githubUrl"])
            if model_data.get("liveUrl") is not None:
                model_data["liveUrl"] = str(model_data["liveUrl"])
            
            # Create SQLAlchemy model instance
            db_project = Project(**model_data) 
            projects_to_add.append(db_project)
            # --------------------------------------------- #
            projects_created_count += 1
        else:
            logger.info(f"Project with ID {project_id} already exists, skipping creation.")
            
    # Add and commit outside the loop if there are new projects
    if projects_to_add:
        logger.info(f"Adding {len(projects_to_add)} new projects to the session...")
        db.add_all(projects_to_add)
        try:
            await db.commit()
            logger.info("Commit of new projects successful.")
            # Optional: Refresh if you need the updated objects
            # for proj in projects_to_add:
            #     await db.refresh(proj)
        except Exception as e:
            logger.error(f"Error during commit of initial projects: {e}", exc_info=True)
            await db.rollback() # Revert if the commit fails
            raise # Re-raise the error so it's visible in the lifespan
            
    logger.info(f"{projects_created_count} new projects were created.")

    # --- Populate Blog Posts ---
    logger.info("Checking/populating initial blog posts...")
    posts_created_count = 0
    posts_to_add = [] # List to add in batch
    
    for post_data in initial_data.initial_blog_posts:
        post_id = post_data.get("id") # ID is a string here
        if not post_id:
            logger.warning(f"Post in initial_data without ID, skipping: {post_data.get('title')}")
            continue
        
        # Use the get_blog_post function that already exists (does it assume ID is int? Check model)
        # We need to ensure the ID used for the search matches the type of the model's PK
        # Read BlogPost model to verify PK type (id)
        # *** ASSUMING BlogPost model has id as a String PK ***
        # If it were an int, we would need to convert post_id to int here.
        existing_post = await db.get(BlogPost, post_id) # Use db.get directly if PK is simple
        # Or if get_blog_post expects int: await crud.blog.get_blog_post(db, blog_post_id=int(post_id)) 
        
        if not existing_post:
            logger.info(f"Preparing to create post with ID: {post_id}")
            
            # Create BlogPost MODEL instance directly
            model_data = post_data.copy()
            
            # Ensure 'date' is a date/datetime object compatible with SQLAlchemy
            # initial_data uses datetime.date, which should be compatible with SQLA Date
            if "date" in model_data and not isinstance(model_data["date"], date):
                 logger.warning(f"The 'date' field for post {post_id} is not a date object: {type(model_data['date'])}. Attempting to continue.")
                 # We could try to convert it if it's a string: model_data["date"] = date.fromisoformat(model_data["date"])
            
            # Create the model instance
            # We need to add author_id if the model requires it and it's not in initial_data
            # For now, we assume it's not strictly necessary here or will be handled with a default
            # If the model has a mandatory author_id, this will fail
            if "author_id" not in model_data:
                 model_data["author_id"] = 1 # Or the default superuser ID
                 logger.warning(f"Assigning default author_id=1 to post {post_id}")
            
            # Create BlogPost instance
            try:
                 db_post = BlogPost(**model_data) 
                 posts_to_add.append(db_post)
                 posts_created_count += 1
            except Exception as e:
                 logger.error(f"Error creating BlogPost model instance for ID {post_id}: {e}", exc_info=True)

        else:
            logger.info(f"Post with ID {post_id} already exists, skipping creation.")

    # Add and commit outside the loop if there are new posts
    if posts_to_add:
        logger.info(f"Adding {len(posts_to_add)} new blog posts to the session...")
        db.add_all(posts_to_add)
        try:
            await db.commit()
            logger.info("Commit of new blog posts successful.")
        except Exception as e:
            logger.error(f"Error during commit of initial posts: {e}", exc_info=True)
            await db.rollback()
            raise
            
    logger.info(f"{posts_created_count} new blog posts were created.")
    
    # --- Populate other data if necessary ---
    
    logger.info("Database initialization completed.") 