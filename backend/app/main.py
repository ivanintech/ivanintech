import sys
from pathlib import Path
import traceback
from datetime import datetime, timezone, timedelta

# Add project root to PYTHONPATH
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

import sentry_sdk
from fastapi import FastAPI, Depends, APIRouter
from fastapi.routing import APIRoute
from starlette.routing import Mount
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
import logging
import asyncio

# --- Project Imports ---
from app.api.main import api_router
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.db import seed_db, base  # noqa: F401
from app.services.aggregated_news_service import fetch_and_store_news
from app.services.blog_automation_service import (
    run_blog_draft_generation as blog_draft_generation_job,
)
from app import crud

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- FastAPI Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events for the application.
    """
    logger.info("--- Application Starting Up ---")
    
    # --- Setup Scheduler ---
    db_uri_str = str(settings.SQLALCHEMY_DATABASE_URI)
    # This logic correctly handles both PostgreSQL for production and SQLite for local dev
    if "postgresql" in db_uri_str:
        sync_db_url = db_uri_str.replace("postgresql+asyncpg", "postgresql+psycopg")
    else:
        sync_db_url = db_uri_str.replace("sqlite+aiosqlite", "sqlite")
        
    logger.info(f"Using sync DB URL for APScheduler JobStore: {sync_db_url}")
    
    scheduler = AsyncIOScheduler(jobstores={'default': SQLAlchemyJobStore(url=sync_db_url)})
    # Schedule the news fetching job to run every 6 hours
    scheduler.add_job(
        run_fetch_news_job,
        "interval",
        hours=6,
        id="fetch_news_job",
        replace_existing=True,
        next_run_time=datetime.now(timezone.utc) + timedelta(seconds=20),
    )
    # Schedule the blog draft generation job to run once a day
    scheduler.add_job(
        run_blog_draft_job,
        "interval",
        days=1,
        id="run_blog_draft_generation_job",
        replace_existing=True,
        next_run_time=datetime.now(timezone.utc) + timedelta(seconds=30), # Delay start
    )

    scheduler.start()
    logger.info("APScheduler started with background jobs.")

    # --- Database Seeding ---
    # This is the main part: we call our seed_data function to populate the DB.
    logger.info("Checking and seeding database with initial data...")
    if settings.RUN_DB_RESET_ON_STARTUP:
        logger.warning("--- RUN_DB_RESET_ON_STARTUP is TRUE: Cleaning database before seeding. ---")
        async with AsyncSessionLocal() as db:
            try:
                await seed_db.clean_database(db)
                await seed_db.seed_data(db)
                logger.info("Database reset and seeding process completed.")
            except Exception as e:
                logger.error(f"Error during database reset and seed: {e}", exc_info=True)
    else:
        logger.info("--- RUN_DB_RESET_ON_STARTUP is FALSE: Synchronizing database without cleaning. ---")
    async with AsyncSessionLocal() as db:
        try:
            await seed_db.seed_data(db)
            logger.info("Database synchronization process completed.")
        except Exception as e:
            logger.error(f"Error during database synchronization: {e}", exc_info=True)

    # --- Initial Background Tasks ---
    logger.info("Scheduling non-critical background tasks...")
    asyncio.create_task(load_initial_data_background())
    
    yield
    
    logger.info("--- Application Shutting Down ---")
    scheduler.shutdown(wait=True)
    logger.info("APScheduler shut down gracefully.")


# --- Custom Unique ID Function for OpenAPI ---
def custom_generate_unique_id(route: APIRoute) -> str:
    tag = route.tags[0] if route.tags else "default"
    return f"{tag}-{route.name}"


# --- Sentry Initialization ---
if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)


# --- FastAPI App Instantiation ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan
)


# --- Middlewares ---
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"***** Petición Recibida: {request.method} {request.url.path} *****")
    response = await call_next(request)
    logger.info(f"***** Petición Procesada: {request.method} {request.url.path} - Status: {response.status_code} *****")
    return response

effective_cors_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:8000",
    "https://ivanintech-frontend.onrender.com",
    "https://ivanintech.com",
    "https://www.ivanintech.com",
]
logger.info(f"[CORS Setup] Effective origins: {effective_cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=effective_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- API Routers ---
app.include_router(api_router, prefix=settings.API_V1_STR)


# --- Root Endpoint ---
@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}


# --- Async Helper Functions for Scheduler ---
async def run_fetch_news_job():
    """Helper function to create a DB session for the news fetching job."""
    logger.info("--- [JOB] Running scheduled news fetching job... ---")
    async with AsyncSessionLocal() as session:
        try:
            superuser = await crud.user.get_by_email(db=session, email=settings.FIRST_SUPERUSER)
            if superuser:
                await fetch_and_store_news(db=session, user=superuser)
            else:
                logger.error("[JOB] Could not fetch news: Superuser not found.")
        except Exception as e:
            logger.error(f"[JOB] Error during scheduled news fetch: {e}", exc_info=True)

async def run_blog_draft_job():
    """Helper function to create a DB session for the blog draft generation job."""
    logger.info("--- [JOB] Running scheduled blog draft generation job... ---")
    async with AsyncSessionLocal() as session:
        try:
            await blog_draft_generation_job(db=session)
        except Exception as e:
            logger.error(f"[JOB] Error during scheduled blog draft generation: {e}", exc_info=True)

async def load_initial_data_background():
    """
    A background task to run non-critical startup operations
    like fetching news without blocking the main application.
    """
    logger.info("Scheduling non-critical background tasks...")
    # Give the application a moment to fully initialize
    await asyncio.sleep(10)
    
    async with AsyncSessionLocal() as session:
        try:
            logger.info("Executing one-time background task: fetch_and_store_news...")
            
            # Get the first superuser to associate news with
            superuser = await crud.user.get_by_email(db=session, email=settings.FIRST_SUPERUSER)
            if not superuser:
                logger.error("Could not fetch news: Superuser not found in the database.")
                return

            await fetch_and_store_news(db=session, user=superuser)
            
        except Exception as e:
            logger.error(f"Error during initial background news fetch: {e}")
            traceback.print_exc()

# --- Main Entry Point ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
