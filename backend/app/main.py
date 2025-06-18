import sys
from pathlib import Path

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
from app.services.aggregated_news_service import fetch_and_store_news
from app.services.blog_automation_service import run_blog_draft_generation
from app.db.seed_db import seed_data # Our new seeding function

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
    scheduler.add_job(fetch_news_job, 'interval', hours=1, id='fetch_news_job', replace_existing=True)
    scheduler.add_job(run_blog_draft_generation_job, 'cron', hour=12, minute=0, id='blog_draft_job', replace_existing=True)
    scheduler.start()
    logger.info("APScheduler started with background jobs.")

    # --- Database Seeding ---
    # This is the main part: we call our seed_data function to populate the DB.
    logger.info("Checking and seeding database with initial data...")
    async with AsyncSessionLocal() as db:
        try:
            await seed_data(db)
            logger.info("Database seeding process completed.")
        except Exception as e:
            logger.error(f"Error during database seeding: {e}", exc_info=True)
            # We don't re-raise the exception to allow the app to start even if seeding fails.
            # Render might restart it, giving it another chance.

    # --- Initial Background Tasks ---
    logger.info("Scheduling non-critical background tasks...")
    asyncio.create_task(load_initial_data_background())
    
    yield
    
    logger.info("--- Application Shutting Down ---")
    scheduler.shutdown()
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
async def fetch_news_job():
    logger.info("Running scheduled job: fetch_and_store_news")
    try:
        await fetch_and_store_news()
    except Exception as e:
        logger.error(f"Error in scheduled news fetch: {e}", exc_info=True)

async def run_blog_draft_generation_job():
    logger.info("Running scheduled job: run_blog_draft_generation")
    async with AsyncSessionLocal() as db:
        try:
            await run_blog_draft_generation(db)
        except Exception as e:
            logger.error(f"Error in scheduled blog draft generation: {e}", exc_info=True)

async def load_initial_data_background():
    """Runs non-critical tasks in the background on startup."""
    logger.info("Executing one-time background task: fetch_and_store_news...")
    try:
        await fetch_and_store_news()
    except Exception as e:
        logger.error(f"Error during initial background news fetch: {e}", exc_info=True)

# --- Main Entry Point ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
