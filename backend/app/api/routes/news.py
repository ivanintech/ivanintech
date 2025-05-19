import logging # Importar logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timezone, timedelta

# from app.schemas.news_item import NewsItemRead # Ajusta según la estructura de tu schema -> Incorrect Path
from app.schemas.news import NewsItemRead, NewsItemCreate # Correct path
from app.db.session import get_db
# from app.services.news_service import fetch_ai_news # Import the new service -> Incorrecto
from app.crud import crud_news
from app.db.models.user import User # User model is in app.db.models.user
from app.api import deps # Import deps for authentication

# Configurar logger básico (se puede hacer más complejo si se necesita)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("", response_model=List[NewsItemRead])
@router.get("/", response_model=List[NewsItemRead])
async def read_news(
    skip: int = 0,
    limit: int = 10,
    # sector: Optional[str] = None, # Ya no se usa aquí
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve news items from the last month.
    """
    # logger.info(f"[API] Recibida petición a /news/?skip={skip}&limit={limit}&sector={sector}")
    logger.info(f"[API] Recibida petición a /news/?skip={skip}&limit={limit}") # Log actualizado
    try:
        # Calcular fecha de hace un mes
        # one_month_ago = datetime.now(timezone.utc) - timedelta(days=30) # Ya no se usa aquí
        
        # Llamar a CRUD sin filtro de fecha (o añadirlo si se reimplementa en CRUD)
        news_items = await crud_news.get_news_items(
            db=db, 
            skip=skip, 
            limit=limit
            # start_date=one_month_ago # <-- ELIMINADO
            # time_category=time_category, # Eliminado
            # sector=sector # Eliminado
        ) 
        # logger.info(f"[API] Devolviendo {len(news_items)} noticias (último mes).") # <-- Log actualizado
        logger.info(f"[API] Devolviendo {len(news_items)} noticias.") # Log ajustado
        return news_items
    except Exception as e:
        # Registrar el traceback completo del error
        logger.error(f"Error fetching news items: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error fetching news")

@router.post("/", response_model=NewsItemRead, status_code=201)
async def create_news_item(
    *,
    db: AsyncSession = Depends(get_db),
    news_item_in: NewsItemCreate,
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Create new news item. Superuser only.
    """
    logger.info(f"[API] User {current_user.email} creating news item: {news_item_in.title}")
    try:
        news_item = await crud_news.create_news_item(db=db, obj_in=news_item_in)
        logger.info(f"[API] News item '{news_item.title}' created successfully with id {news_item.id}")
        return news_item
    except Exception as e:
        logger.error(f"Error creating news item: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error creating news item")

# ... (otras rutas si existen) ... 