import logging # Importar logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timezone, timedelta

# from app.schemas.news_item import NewsItemRead # Ajusta según la estructura de tu schema -> Incorrect Path
from app.schemas.news import NewsItemRead # Correct path
from app.db.session import get_db
# from app.services.news_service import fetch_ai_news # Import the new service -> Incorrecto
from app.crud import crud_news

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

# ... (otras rutas si existen) ... 