import sys
from pathlib import Path
import traceback
from datetime import datetime, timezone, timedelta
import os
import nest_asyncio

from app.scripts import seed_db
# nest_asyncio.apply()  # Comentado temporalmente para evitar conflicto con uvloop

# Add project root to PYTHONPATH
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

# Apply the asyncio patch for Windows BEFORE any other imports that might use it
# from pre_run_patch import apply_windows_asyncio_patch
# apply_windows_asyncio_patch()

import sentry_sdk
from fastapi import FastAPI, Depends, APIRouter, Request
from fastapi.routing import APIRoute
from starlette.routing import Mount
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
import logging
import asyncio
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from logging.handlers import SMTPHandler
from fastapi.middleware.gzip import GZipMiddleware

# --- Global Variables ---
scheduler = None  # Will be initialized in lifespan

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure logging to be less verbose for third-party libraries
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("google.api_core").setLevel(logging.WARNING)
logging.getLogger("apscheduler.executors.default").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# --- Configuración de alertas por email para errores críticos usando variables de entorno ---
# TEMPORARILY DISABLED due to SMTP authentication issues
# mail_handler = SMTPHandler(
#     mailhost=(os.getenv("MAIL_SERVER"), int(os.getenv("MAIL_PORT", "587"))),
#     fromaddr=os.getenv("MAIL_FROM"),
#     toaddrs=[os.getenv("MAIL_FROM")],
#     subject="[ALERTA] Error crítico en Iván In Tech",
#     credentials=(os.getenv("MAIL_USERNAME"), os.getenv("MAIL_PASSWORD")),
#     secure=() if os.getenv("MAIL_STARTTLS", "False") == "True" else None
# )
# mail_handler.setLevel(logging.ERROR)
# logging.getLogger().addHandler(mail_handler)

# --- Project Imports ---
from app.api.main import api_router
from app.core.config import settings
from app.db.session import async_session_maker
from app.db import base  # noqa: F401
from app.services.aggregated_news_service import fetch_and_store_news
from app.services.blog_automation_service import (
    run_blog_draft_generation as blog_draft_generation_job,
)
from app.services.keep_alive_service import start_keep_alive_service, stop_keep_alive_service
from app import crud


# --- FastAPI Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events for the application.
    """
    global scheduler  # Declare global at the beginning
    
    logger.info("--- Application Starting Up ---")
    
    # --- Setup Scheduler ---
    # Using simplified scheduler configuration for Supabase compatibility
    logger.info("Setting up APScheduler for automated news fetching...")
    
    try:
        # Use memory-based job store instead of database to avoid connection issues
        from apscheduler.jobstores.memory import MemoryJobStore
        scheduler = AsyncIOScheduler(jobstores={'default': MemoryJobStore()})
        
        # Schedule the news fetching job to run every 6 hours (4 times per day)
        # This ensures news are updated more frequently
        scheduler.add_job(
            run_fetch_news_job,
            "interval",
            hours=6,
            id="fetch_news_job",
            replace_existing=True,
        )
        
        # Also schedule a daily cleanup at 2:00 AM Spanish time
        scheduler.add_job(
            run_news_cleanup_job,
            "cron",
            hour=2,
            minute=0,
            id="run_news_cleanup_job",
            replace_existing=True,
            timezone="Europe/Madrid",
        )

        scheduler.start()
        logger.info("APScheduler started with background jobs using memory job store.")
        
        # Execute news fetch immediately on startup
        logger.info("Executing initial news fetch on startup...")
        asyncio.create_task(run_fetch_news_job())
        
    except Exception as e:
        logger.error(f"Failed to start APScheduler: {e}")
        logger.info("Continuing without scheduler - manual news fetching still available.")

    # --- Database Seeding ---
    # This is the main part: we call our seed_data function to populate the DB.
    # TEMPORARILY DISABLED FOR TESTING
    # logger.info("Checking and seeding database with initial data...")
    # if settings.RUN_DB_RESET_ON_STARTUP:
    #     logger.warning("--- RUN_DB_RESET_ON_STARTUP is TRUE: Cleaning database before seeding. ---")
    #     async with async_session_maker() as db:
    #         try:
    #             await seed_db.clean_database(db)
    #             await seed_db.seed_data(db)
    #             logger.info("Database reset and seeding process completed.")
    #         except Exception as e:
    #             logger.error(f"Error during database reset and seed: {e}", exc_info=True)
    # else:
    #     logger.info("--- RUN_DB_RESET_ON_STARTUP is FALSE: Synchronizing database without cleaning. ---")
    # async with async_session_maker() as db:
    #     try:
    #         await seed_db.seed_data(db)
    #         logger.info("Database synchronization process completed.")
    #     except Exception as e:
    #         logger.error(f"Error during database synchronization: {e}", exc_info=True)
    
    logger.info("Database seeding temporarily disabled for testing.")

    # --- Keep-Alive Service ---
    # Start keep-alive service to prevent Render from sleeping
    logger.info("Starting keep-alive service for Render...")
    await start_keep_alive_service()
    
    # --- Initial Background Tasks ---
    # Schedule the task to run after the app has fully started up
    logger.info("Scheduling non-critical background tasks to run post-startup.")
    asyncio.create_task(load_initial_data_background())
    
    yield
    
    logger.info("--- Application Shutting Down ---")
    
    # Stop keep-alive service
    await stop_keep_alive_service()
    
    try:
        if scheduler:
            scheduler.shutdown(wait=True)
            logger.info("APScheduler shut down gracefully.")
    except:
        logger.info("APScheduler was not running or already shut down.")


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
    lifespan=lifespan,
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Asegúrate de que los directorios para archivos estáticos existan y monta el directorio
os.makedirs("app/static/avatars", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# --- Middlewares ---
# El middleware de log de peticiones se ha eliminado para reducir la verbosidad.
# Uvicorn ya proporciona logs de acceso estándar que son suficientes.

# Registra las configuraciones de CORS al iniciar
logger.info(f"CORS origins loaded from settings: {settings.BACKEND_CORS_ORIGINS}")
logger.info(f"Frontend host from settings: {settings.FRONTEND_HOST}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.all_cors_origins,  # Usa la lista de settings
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

# --- Health Check Endpoint ---
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    try:
        # Verificar conexión a la base de datos
        async with async_session_maker() as db:
            await db.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": settings.PROJECT_NAME,
            "version": "1.0.0"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service": settings.PROJECT_NAME
            }
        )

# --- Keep-Alive Endpoint ---
@app.get("/keep-alive")
async def keep_alive():
    """Simple keep-alive endpoint for Render to prevent sleep."""
    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": "Service is running and responsive",
        "render": os.getenv("RENDER", "false"),
        "environment": os.getenv("ENVIRONMENT", "unknown")
    }


# --- Async Helper Functions for Scheduler ---
async def run_fetch_news_job():
    """Helper function to create a DB session for the news fetching job."""
    logger.info("--- [JOB] Running scheduled news fetching job... ---")
    async with async_session_maker() as session:
        try:
            superuser = await crud.user.get_by_email(db=session, email=settings.FIRST_SUPERUSER)
            if superuser:
                await fetch_and_store_news(user=superuser)
            else:
                logger.error("[JOB] Could not fetch news: Superuser not found.")
        except Exception as e:
            logger.error(f"[JOB] Error during scheduled news fetch: {e}", exc_info=True)

async def run_blog_draft_job():
    """Helper function to create a DB session for the blog draft generation job."""
    logger.info("--- [JOB] Running scheduled blog draft generation job... ---")
    async with async_session_maker() as session:
        try:
            await blog_draft_generation_job(db=session)
        except Exception as e:
            logger.error(f"[JOB] Error during scheduled blog draft generation: {e}", exc_info=True)

async def run_news_cleanup_job():
    """Helper function to create a DB session for the news cleanup job."""
    logger.info("--- [JOB] Running scheduled news cleanup job... ---")
    async with async_session_maker() as session:
        try:
            from app.scripts.cleanup_old_news import cleanup_old_news
            
            # Limpiar noticias más antiguas de 30 días
            result = await cleanup_old_news(days_to_keep=30)
            logger.info(f"[JOB] News cleanup completed: {result['deleted_count']} items deleted")
            
        except Exception as e:
            logger.error(f"[JOB] Error during scheduled news cleanup: {e}", exc_info=True)

async def load_initial_data_background():
    """
    A background task to run non-critical startup operations
    like fetching news without blocking the main application.
    """
    # Give the application a moment to fully initialize to prevent race conditions
    await asyncio.sleep(10)
    
    logger.info("Executing one-time background task: fetch_and_store_news...")
    
    async with async_session_maker() as session:
        try:
            superuser = await crud.user.get_by_email(db=session, email=settings.FIRST_SUPERUSER)
            if superuser:
                await fetch_and_store_news(user=superuser)
            else:
                logger.error("Could not fetch news on startup: Superuser not found.")
        except Exception as e:
            # Log the full traceback for detailed debugging
            logger.error(f"Error during initial background news fetch: {e}", exc_info=True)


# --- Main Entry Point ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
