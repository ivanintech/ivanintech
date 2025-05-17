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

# --- Importar Routers Individuales ---
from app.api.routes import login, utils, portfolio, blog, news, contact # <-- Importar directamente
# -------------------------------------

from app.core.config import settings
from app.db.session import get_db, AsyncSessionLocal
from app.services.aggregated_news_service import fetch_and_store_news
from app.services.blog_automation_service import run_blog_draft_generation
from app.db.init_db import init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Lifespan Definition (Moved Before App Instantiation) --- #
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application lifespan...")
    # Ensure 'alembic upgrade head' is run before starting.
    
    # --- Configuración del Job Store para APScheduler ---
    # Crear URL síncrona (reemplazando 'sqlite+aiosqlite' por 'sqlite')
    sync_db_url = settings.SQLALCHEMY_DATABASE_URI.replace("sqlite+aiosqlite", "sqlite")
    logger.info(f"Using sync DB URL for APScheduler JobStore: {sync_db_url}")
    
    # Crear engine SÍNCRONO específicamente para el JobStore
    sync_engine = create_engine(sync_db_url)
    
    jobstores = {
        # Pasar el engine SÍNCRONO al SQLAlchemyJobStore
        'default': SQLAlchemyJobStore(engine=sync_engine)
    }
    scheduler = AsyncIOScheduler(jobstores=jobstores)

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
    # Usar AsyncSessionLocal para obtener una sesión dentro del lifespan
    async with AsyncSessionLocal() as db:
        try:
            await init_db(db)
            logger.info("Database initialization finished.")
        except Exception as e:
            logger.error(f"Error during database initialization: {e}", exc_info=True)
            # Considerar si se debe detener el inicio de la app aquí
    # --- Fin Inicialización DB --- #
    
    # --- Ejecución ÚNICA del servicio de noticias al inicio (PARA PRUEBAS) ---
    print("Ejecutando fetch_and_store_news una vez al inicio...")
    try:
        await fetch_and_store_news()
        print("Ejecución inicial de fetch_and_store_news completada.")
    except Exception as e:
        print(f"Error durante la ejecución inicial de fetch_and_store_news: {e}")
    # --- Fin de ejecución única ---
    
    yield
    logger.info("Shutting down application lifespan...")
    scheduler.shutdown()
    logger.info("APScheduler shut down.")
    # Eliminar también el engine síncrono
    sync_engine.dispose()
    logger.info("Sync database engine for JobStore disposed.")
    # NOTA: No necesitamos eliminar el engine asíncrono aquí, 
    # ya que no lo creamos explícitamente en lifespan. 
    # Se maneja a través de AsyncSessionLocal.

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
# Asegurarse de que los orígenes sean una lista de strings
origins_as_strings: list[str] = []
if settings.BACKEND_CORS_ORIGINS:
    if isinstance(settings.BACKEND_CORS_ORIGINS, list):
        for origin_item in settings.BACKEND_CORS_ORIGINS: # Renombrar variable para claridad
            # Convertir AnyUrl (o lo que sea) a str y quitar trailing slash
            origins_as_strings.append(str(origin_item).rstrip('/')) 
    elif isinstance(settings.BACKEND_CORS_ORIGINS, str): # Si es un solo string separado por comas desde el .env
        # Dividir por comas, quitar espacios y trailing slashes
        origins_as_strings = [o.strip().rstrip('/') for o in settings.BACKEND_CORS_ORIGINS.split(',')]
    # else: # Si es un solo AnyUrl (no una lista) y no un string, caso menos común con Pydantic BaseSettings desde .env
        # Aún así, convertirlo a string y limpiar
        # origins_as_strings.append(str(settings.BACKEND_CORS_ORIGINS).rstrip('/'))

# Fallback si la lista está vacía después del procesamiento (o si BACKEND_CORS_ORIGINS no estaba definido)
if not origins_as_strings:
    logger.warning("BACKEND_CORS_ORIGINS no está configurado o resultó en una lista vacía. Usando fallback: ['http://localhost:3000']")
    origins_as_strings = ["http://localhost:3000"] # Un fallback seguro para desarrollo

print(f"[CORS Setup] Effective origins being used: {origins_as_strings}") # Log para ver qué se usa realmente

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins_as_strings, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routers --- #
# --- Restaurados ---
app.include_router(login.router, prefix=settings.API_V1_STR, tags=["login"]) # /api/v1
app.include_router(utils.router, prefix=f"{settings.API_V1_STR}/utils", tags=["utils"]) # /api/v1/utils
app.include_router(portfolio.router, prefix=f"{settings.API_V1_STR}/portfolio", tags=["portfolio"]) # /api/v1/portfolio
app.include_router(blog.router, prefix=f"{settings.API_V1_STR}/content", tags=["content"]) # /api/v1/content
app.include_router(news.router, prefix=f"{settings.API_V1_STR}/news", tags=["content"])
app.include_router(contact.router, prefix=f"{settings.API_V1_STR}/contact", tags=["contact"]) # /api/v1/contact
# ------------------------------------

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

# La definición de lifespan se ha movido antes de la instanciación de app
