import sentry_sdk
from fastapi import FastAPI, Depends, APIRouter
from fastapi.routing import APIRoute
from starlette.routing import Mount
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import create_engine # Importar create_engine síncrono
import logging
# Import anext if available (Python 3.10+), otherwise handle StopAsyncIteration
try:
    from asyncio import anext
except ImportError:
    # Basic fallback for older versions or if anext is not directly available
    # This might need adjustment based on exact Python version/setup
    async def anext(ait): 
        return await ait.__anext__()

# --- Importar el api_router principal desde app.api.main --- # 
from app.api.main import api_router # <-- MODIFICADO
# -------------------------------------

from app.core.config import settings
from app.db.session import get_db, AsyncSessionLocal # Corrected import
from app.services.aggregated_news_service import fetch_and_store_news
from app.services.blog_automation_service import run_blog_draft_generation
from app.db.init_db import init_db
# from app.services.resource_service import process_initial_resources # Importar el nuevo servicio
# from app.services.project_service import process_initial_projects # Importar para proyectos
import asyncio # Importar asyncio
# from app.api.routes import login, users, news, resource_links, blog, contact, health # Removed webhooks from import
from app.api.routes import login, users, news, resource_links, blog, contact # Removed health from import
from app.api.routes import projects # Import the new projects router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Lifespan Definition (Moved Before App Instantiation) --- #
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application lifespan...")
    
    # --- Configuración del Job Store para APScheduler ---
    # Forzar la creación de una URL de base de datos síncrona para APScheduler
    db_uri_str = str(settings.SQLALCHEMY_DATABASE_URI)
    if "postgresql" in db_uri_str:
        # Reemplaza 'postgresql+asyncpg' con 'postgresql' para la conexión síncrona
        sync_db_url = db_uri_str.replace("+asyncpg", "")
    else:
        # Mantiene la lógica para SQLite u otros
        sync_db_url = db_uri_str.replace("sqlite+aiosqlite", "sqlite")

    logger.info(f"Using sync DB URL for APScheduler JobStore: {sync_db_url}")
    
    scheduler = AsyncIOScheduler(jobstores={
        'default': SQLAlchemyJobStore(url=sync_db_url)
    })

    # Schedule the news aggregation job
    scheduler.add_job(
        fetch_news_job, 
        'interval', 
        hours=1, 
        id='fetch_news_job', 
        replace_existing=True
    )
    logger.info("Scheduled news aggregation job to run every hour.")

    # Schedule the blog draft generation job
    scheduler.add_job(
        run_blog_draft_generation_job, 
        'cron', 
        hour=12, 
        minute=0,
        id='blog_draft_job', 
        replace_existing=True
    )
    logger.info("Scheduled blog draft generation job to run daily at 12:00.")

    scheduler.start()
    logger.info("APScheduler started.")
    
    # --- Inicializar Base de Datos --- #
    logger.info("Running database initialization...")
    async with AsyncSessionLocal() as db:
        try:
            await init_db(db)
            logger.info("Database initialization finished.")
        except Exception as e:
            logger.error(f"Error during database initialization: {e}", exc_info=True)
    # --- Fin Inicialización DB --- #
    
    # --- Ejecutar tareas de carga inicial en segundo plano ---
    logger.info("Scheduling background tasks for initial data loading...")
    asyncio.create_task(load_initial_data())
    # --- Fin de ejecución única en segundo plano ---
    
    yield
    logger.info("Shutting down application lifespan...")
    scheduler.shutdown()
    logger.info("APScheduler shut down.")

# --- Custom Unique ID Function --- #
def custom_generate_unique_id(route: APIRoute) -> str:
    tag = route.tags[0] if route.tags else "default"
    return f"{tag}-{route.name}"

# --- Sentry Initialization --- #
if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

# --- FastAPI App Instantiation --- #
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id, # <-- Restaurado
    lifespan=lifespan # <-- Restaurado
)

# --- Log para depuración de CORS ---
# print("[CORS DEBUG] BACKEND_CORS_ORIGINS:", settings.BACKEND_CORS_ORIGINS, type(settings.BACKEND_CORS_ORIGINS)) # Comentado ya que lo manejaremos explícitamente

# --- Middleware para Loguear Peticiones (AÑADIDO PARA DEBUG) ---
from starlette.requests import Request

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"***** Petición Recibida: {request.method} {request.url.path} *****")
    response = await call_next(request)
    logger.info(f"***** Petición Procesada: {request.method} {request.url.path} - Status: {response.status_code} *****")
    return response
# --- FIN Middleware ---

# --- Middleware para CORS ---
# # Asegurarse de que los orígenes sean una lista de strings
# origins_as_strings: list[str] = []
# if settings.BACKEND_CORS_ORIGINS:
#     if isinstance(settings.BACKEND_CORS_ORIGINS, list):
#         for origin_item in settings.BACKEND_CORS_ORIGINS: # Renombrar variable para claridad
#             # Convertir AnyUrl (o lo que sea) a str y quitar trailing slash
#             origins_as_strings.append(str(origin_item).rstrip(\'/\')) 
#     elif isinstance(settings.BACKEND_CORS_ORIGINS, str): # Si es un solo string separado por comas desde el .env
#         # Dividir por comas, quitar espacios y trailing slashes
#         origins_as_strings = [o.strip().rstrip(\'/\') for o in settings.BACKEND_CORS_ORIGINS.split(',')]
#     # else: # Si es un solo AnyUrl (no una lista) y no un string, caso menos común con Pydantic BaseSettings desde .env
#         # Aún así, convertirlo a string y limpiar
#         # origins_as_strings.append(str(settings.BACKEND_CORS_ORIGINS).rstrip(\'/\'))

# # Fallback si la lista está vacía después del procesamiento (o si BACKEND_CORS_ORIGINS no estaba definido)
# if not origins_as_strings:
#     logger.warning("BACKEND_CORS_ORIGINS no está configurado o resultó en una lista vacía. Usando fallback: [\'http://localhost:3000\']")
#     origins_as_strings = ["http://localhost:3000"] # Un fallback seguro para desarrollo

# print(f"[CORS Setup] Effective origins being used: {origins_as_strings}") # Log para ver qué se usa realmente

# Usar directamente la lista de orígenes procesada desde settings
effective_cors_origins = settings.all_cors_origins
logger.info(f"[CORS Setup] Effective origins being used from settings.all_cors_origins: {effective_cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=effective_cors_origins, # Usar la lista unificada
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Router Includes --- #
api_router = APIRouter()
api_router.include_router(login.router)
# api_router.include_router(login.router, prefix="/auth", tags=["Auth"]) # THIS IS THE LINE TO REMOVE/COMMENT
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(news.router, prefix="/news", tags=["News"])
api_router.include_router(projects.router, prefix="/portfolio/projects", tags=["Portfolio Projects"]) # Add projects router
api_router.include_router(resource_links.router, prefix="/resource-links", tags=["Resource Links"])
api_router.include_router(blog.router, prefix="/blog", tags=["Blog"])
# api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"]) # Commented out webhook router
api_router.include_router(contact.router, prefix="/contact", tags=["Contact"])
@api_router.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}

app.include_router(api_router, prefix=settings.API_V1_STR)

# --- Root Endpoint --- #
@app.get("/")
async def root():
    return {"message": f"Bienvenido a {settings.PROJECT_NAME}"}

# Helper async functions to pass to scheduler
async def fetch_news_job():
    logger.info("Running scheduled job: fetch_and_store_news")
    try:
        await fetch_and_store_news()
        logger.info("Finished job: fetch_and_store_news")
    except Exception as e:
        logger.error(f"Error during scheduled news fetch: {e}", exc_info=True)

async def run_blog_draft_generation_job():
    logger.info("Running scheduled job: run_blog_draft_generation")
    async with AsyncSessionLocal() as db:
        try:
            await run_blog_draft_generation(db)
            logger.info("Finished job: run_blog_draft_generation")
        except Exception as e:
            logger.error(f"Error during scheduled blog draft generation: {e}", exc_info=True)

async def load_initial_data():
    """Wraps initial data loading functions to be run in the background."""
    logger.info("Executing fetch_and_store_news once at startup in background...")
    try:
        await fetch_and_store_news()
        logger.info("Initial execution of fetch_and_store_news completed.")
    except Exception as e:
        logger.error(f"Error during initial execution of fetch_and_store_news: {e}", exc_info=True)

    # logger.info("Executing process_initial_resources once at startup in background...")
    # try:
    #     async with AsyncSessionLocal() as db: # Obtener nueva sesión de BD para esta tarea
    #         await process_initial_resources(db)
    #     logger.info("Initial execution of process_initial_resources completed.")
    # except Exception as e:
    #     logger.error(f"Error during initial execution of process_initial_resources: {e}", exc_info=True)

    # Calls to process_initial_projects will be removed entirely

# Ensure the main application entry point or further configurations are below
if __name__ == "__main__":
    import uvicorn
    # Asegúrate de que el host y el puerto estén configurados según tus necesidades
    # Por ejemplo, desde settings o directamente aquí.
    # uvicorn.run(app, host=settings.SERVER_HOST, port=settings.SERVER_PORT, reload=True)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
