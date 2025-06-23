import logging # Import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import trafilatura # Importar trafilatura aquí también
from bs4 import BeautifulSoup # Import BeautifulSoup for parsing HTML
import uuid

# from app.schemas.news_item import NewsItemRead # Adjust according to your schema structure -> Incorrect Path
from app.schemas.news import NewsItemRead, NewsItemCreate, NewsItemSubmit, NewsItemUpdate # Correct path
from app.api import deps # Import deps for authentication
from app import crud
from app.db.models.user import User # User model is in app.db.models.user
from app.services.gemini_service import GeminiService
from app.utils import is_valid_image_url # Importar la función de validación
from app.services import youtube_service # Importar el servicio de YouTube

# Configure basic logger (can be made more complex if needed)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/sectors/top", response_model=List[str])
async def get_top_sectors_route(
    limit: int = 10,
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Get the most frequent sectors from all news items.
    """
    logger.info(f"[API] Received request for top {limit} sectors.")
    try:
        top_sectors = await crud.news.get_top_sectors(db=db, limit=limit)
        logger.info(f"[API] Returning top sectors: {top_sectors}")
        return top_sectors
    except Exception as e:
        logger.error(f"Error fetching top sectors: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error fetching sectors")

@router.get("", response_model=List[NewsItemRead])
@router.get("/", response_model=List[NewsItemRead])
async def read_news(
    skip: int = 0,
    limit: int = 10,
    # sector: Optional[str] = None, # No longer used here
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Retrieve news items.
    """
    logger.info(f"[API] Received request to /news/?skip={skip}&limit={limit}")
    try:
        news_items = await crud.news.get_multi(
            db=db, 
            skip=skip, 
            limit=limit
        ) 
        logger.info(f"[API] Returning {len(news_items)} news items.")
        return news_items
    except Exception as e:
        # Log the full traceback of the error
        logger.error(f"Error fetching news items: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error fetching news")

@router.post("/", response_model=NewsItemRead, status_code=201)
async def create_news_item_route(
    *,
    db: AsyncSession = Depends(deps.get_db),
    news_item_in: NewsItemCreate,
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Create new news item. Superuser only.
    """
    logger.info(f"[API] User {current_user.email} creating news item: {news_item_in.title}")
    try:
        news_item = await crud.news.create(db=db, obj_in=news_item_in)
        logger.info(f"[API] News item '{news_item.title}' created successfully with id {news_item.id}")
        return news_item
    except Exception as e:
        logger.error(f"Error creating news item: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error creating news item")

@router.post("/submit", response_model=NewsItemRead, status_code=201)
async def submit_news_item(
    *,
    db: AsyncSession = Depends(deps.get_db),
    item_in: NewsItemSubmit,
    current_user: User = Depends(deps.get_current_user),
    background_tasks: BackgroundTasks
):
    """
    Submit a new news item from a URL. Logged-in users only.
    The processing is done in the background.
    """
    url = str(item_in.url)
    logger.info(f"User {current_user.email} submitting URL: {url}")
    
    # Check if a news item with this URL already exists
    existing_item = await crud.news.get_by_url(db=db, url=url)
    if existing_item:
        logger.warning(f"URL {url} already exists in the database.")
        raise HTTPException(
            status_code=409,
            detail="This URL has already been submitted."
        )

    gemini_service = GeminiService()

    try:
        # --- Lógica específica para YouTube ---
        video_id = youtube_service._extract_video_id(url)
        youtube_details = None
        if video_id:
            logger.info(f"YouTube video detected. Fetching details for video ID: {video_id}")
            youtube_details = youtube_service.get_youtube_resource_details(url)

        # --- Obtener y analizar contenido ---
        content = await gemini_service.get_content_from_url(url)
        if not content:
            raise HTTPException(status_code=400, detail="Could not retrieve content from the URL.")
        
        # Usar el título de YouTube si está disponible, si no, extraerlo.
        title_for_analysis = youtube_details.title if youtube_details else "Title not available"
        if title_for_analysis == "Title not available":
             soup = BeautifulSoup(content, 'html.parser')
             title_for_analysis = soup.title.string if soup.title else "No Title Found"

        analysis = await gemini_service.evaluate_and_summarize_content(
            title=title_for_analysis,
            content=content
        )

        if not analysis or analysis.get('relevance_rating', 0) < 2.5:
            logger.info(f"URL {url} deemed not relevant or analysis failed.")
            raise HTTPException(
                status_code=400,
                detail="The content of the URL is not considered relevant to AI or could not be analyzed."
            )

        # --- Construir el objeto de noticia ---
        final_title = youtube_details.title if youtube_details else analysis.get('title', 'Title not found')
        final_image_url = youtube_details.thumbnail_url if youtube_details else analysis.get('imageUrl')

        # Validar la URL de la imagen final antes de usarla
        if final_image_url and not await is_valid_image_url(final_image_url):
            logger.warning(f"Invalid image URL '{final_image_url}' for news item. Proceeding without image.")
            final_image_url = None

        news_item_data = NewsItemCreate(
            title=final_title,
            url=url,
            description=analysis.get('summary', ''),
            relevance_rating=analysis.get('relevance_rating'),
            sectors=analysis.get('tags', []),
            sourceName=analysis.get('sourceName', 'YouTube' if youtube_details else None),
            imageUrl=final_image_url,
            is_community=True,
            submitted_by_user_id=current_user.id,
            publishedAt=datetime.now(timezone.utc)
        )
        
        new_news_item = await crud.news.create(db=db, obj_in=news_item_data)
        await db.refresh(new_news_item, ["submitted_by"])
        logger.info(f"Community news item '{new_news_item.title}' created successfully from URL {url}.")
        
        return new_news_item

    except HTTPException as http_exc:
        # Re-raise HTTP exceptions to be handled by FastAPI
        raise http_exc
    except Exception as e:
        logger.error(f"Error processing submitted news URL {url}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing the URL.")

@router.put("/{news_id}", response_model=NewsItemRead)
async def update_news_item(
    *,
    db: AsyncSession = Depends(deps.get_db),
    news_id: uuid.UUID,
    item_in: NewsItemUpdate,
    current_user: User = Depends(deps.get_current_active_superuser),
):
    """
    Update a news item. Superuser only.
    """
    news_item = await crud.news.get(db=db, id=news_id)
    if not news_item:
        raise HTTPException(status_code=404, detail="News item not found")
    
    updated_item = await crud.news.update(db=db, db_obj=news_item, obj_in=item_in)
    return updated_item

@router.delete("/{news_id}", response_model=NewsItemRead)
async def delete_news_item(
    *,
    db: AsyncSession = Depends(deps.get_db),
    news_id: uuid.UUID,
    current_user: User = Depends(deps.get_current_active_superuser),
):
    """
    Delete a news item. Superuser only.
    """
    news_item = await crud.news.get(db=db, id=news_id)
    if not news_item:
        raise HTTPException(status_code=404, detail="News item not found")
    
    deleted_item = await crud.news.remove(db=db, id=news_id)
    return deleted_item

# ... (other routes if they exist) ... 