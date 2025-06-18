import logging # Import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timezone, timedelta

# from app.schemas.news_item import NewsItemRead # Adjust according to your schema structure -> Incorrect Path
from app.schemas.news import NewsItemRead, NewsItemCreate # Correct path
from app.api import deps # Import deps for authentication
from app import crud
from app.db.models.user import User # User model is in app.db.models.user

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
        top_sectors = await crud.news_item.get_top_sectors(db=db, limit=limit)
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
        news_items = await crud.news_item.get_multi(
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
        news_item = await crud.news_item.create(db=db, obj_in=news_item_in)
        logger.info(f"[API] News item '{news_item.title}' created successfully with id {news_item.id}")
        return news_item
    except Exception as e:
        logger.error(f"Error creating news item: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error creating news item")

# ... (other routes if they exist) ... 