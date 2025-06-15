import logging # Import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timezone, timedelta

# from app.schemas.news_item import NewsItemRead # Adjust according to your schema structure -> Incorrect Path
from app.schemas.news import NewsItemRead, NewsItemCreate # Correct path
from app.db.session import get_db
# from app.services.news_service import fetch_ai_news # Import the new service -> Incorrect
from app.crud import crud_news
from app.db.models.user import User # User model is in app.db.models.user
from app.api import deps # Import deps for authentication

# Configure basic logger (can be made more complex if needed)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/sectors/top", response_model=List[str])
async def get_top_sectors_route(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the most frequent sectors from all news items.
    """
    logger.info(f"[API] Received request for top {limit} sectors.")
    try:
        # This logic should ideally be in a crud function, but placed here for now
        sector_subquery = func.jsonb_array_elements_text(NewsItem.sectors).alias("sector")
        stmt = (
            select(sector_subquery)
            .where(NewsItem.sectors.isnot(None)) # Ensure sectors column is not null
            .group_by(sector_subquery)
            .order_by(func.count().desc())
            .limit(limit)
        )
        
        result = await db.execute(stmt)
        top_sectors = result.scalars().all()
        
        logger.info(f"[API] Returning top sectors: {top_sectors}")
        return top_sectors
    except Exception as e:
        logger.error(f"Error fetching top sectors: {e}", exc_info=True)
        # Return an empty list on error to prevent frontend from crashing
        raise HTTPException(status_code=500, detail="Internal server error fetching sectors")

@router.get("", response_model=List[NewsItemRead])
@router.get("/", response_model=List[NewsItemRead])
async def read_news(
    skip: int = 0,
    limit: int = 10,
    # sector: Optional[str] = None, # No longer used here
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve news items.
    """
    logger.info(f"[API] Received request to /news/?skip={skip}&limit={limit}") # Updated log
    try:
        # Call CRUD without date filter
        news_items = await crud_news.get_news_items(
            db=db, 
            skip=skip, 
            limit=limit
        ) 
        logger.info(f"[API] Returning {len(news_items)} news items.") # Adjusted log
        return news_items
    except Exception as e:
        # Log the full traceback of the error
        logger.error(f"Error fetching news items: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error fetching news")

@router.post("/", response_model=NewsItemRead, status_code=201)
async def create_news_item_route(
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
        news_item = await crud_news.create_news_item(db=db, item=news_item_in)
        logger.info(f"[API] News item '{news_item.title}' created successfully with id {news_item.id}")
        return news_item
    except Exception as e:
        logger.error(f"Error creating news item: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error creating news item")

# ... (other routes if they exist) ... 