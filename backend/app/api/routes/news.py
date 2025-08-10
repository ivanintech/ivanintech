import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any, Optional
import uuid
from datetime import datetime, timezone

from app.schemas.news import NewsItemRead, NewsItemCreate, NewsItemSubmit, NewsItemUpdate, PaginatedNews
from app.api import deps
from app import crud
from app.db.models.user import User
from app.services.supabase_service import supabase_service
from app.services.cache_service import cached, get_cached_news_data, cache_news_data, invalidate_news_cache
from app.schemas.submission import SubmissionResponse
from app.schemas.user import UserPublic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/supabase", response_model=List[dict])
async def read_news_supabase(skip: int = 0, limit: int = 10):
    """
    Retrieve news items using Supabase REST API (fallback when PostgreSQL is unavailable).
    """
    logger.info(f"[API News Supabase] Reading news with skip={skip}, limit={limit}")
    try:
        news = await supabase_service.get_news(skip=skip, limit=limit)
        logger.info(f"[API News Supabase] Found {len(news)} news items.")
        return news
    except Exception as e:
        logger.error(f"[API News Supabase] Error reading news: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error fetching news")

@router.get("/sectors/top", response_model=List[str])
async def get_top_sectors_route(db: deps.SessionDep, limit: int = 10):
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

@router.get(
    "/",
    response_model=PaginatedNews,
    summary="Get a paginated list of news items",
)
@cached(ttl_seconds=300, key_prefix="news_list")  # Cache for 5 minutes
async def read_news_items(
    db: deps.SessionDep,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    period: Optional[str] = Query(None, description="Filter by period (currently ignored, kept for compatibility)"),
):
    """
    Retrieve a paginated list of news items with caching for better performance.
    """
    skip = (page - 1) * per_page
    
    # Try to get from cache first for common queries
    if page == 1 and per_page <= 20:
        cached_data = await get_cached_news_data()
        if cached_data:
            logger.info(f"[API News] Cache hit for page {page}, returning cached data")
            return PaginatedNews(**cached_data)
    
    # If not in cache, fetch from database
    logger.info(f"[API News] Cache miss, fetching from database: page={page}, per_page={per_page}")
    total, news_items = await crud.news.get_multi_paginated(
        db, skip=skip, per_page=per_page
    )
    
    items = []
    for item in news_items:
        submitted_by = None
        if item.submitted_by:
            user_dict = {
                "id": item.submitted_by.id,
                "full_name": getattr(item.submitted_by, "full_name", None),
                "avatar_path": getattr(item.submitted_by, "avatar_path", None),
                "website_url": getattr(item.submitted_by, "website_url", None),
            }
            submitted_by = UserPublic.model_validate(user_dict)
        item_dict = item.__dict__.copy()
        item_dict['submitted_by'] = submitted_by
        items.append(NewsItemRead.model_validate(item_dict))
    
    result = PaginatedNews(total=total, items=items)
    
    # Cache the result for first page
    if page == 1 and per_page <= 20:
        await cache_news_data(result.model_dump(), ttl_seconds=300)
    
    return result

@router.post(
    "/",
    response_model=NewsItemRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(deps.get_current_active_superuser)],
)
async def create_news_item(
    *,
    db: deps.SessionDep,
    news_item_in: NewsItemCreate,
    current_user: deps.CurrentUser,
) -> Any:
    """
    Create new news item. Superuser only.
    """
    logger.info(f"[API] User {current_user.email} creating news item: {news_item_in.title}")
    try:
        news_item = await crud.news.create_with_owner(
            db=db, obj_in=news_item_in, user_id=current_user.id
        )
        logger.info(f"[API] News item '{news_item.title}' created successfully with id {news_item.id}")
        return news_item
    except Exception as e:
        logger.error(f"Error creating news item: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error creating news item")

@router.post("/submit", status_code=status.HTTP_202_ACCEPTED)
async def submit_news_item(
    item_in: NewsItemSubmit,
    db: deps.SessionDep,
    current_user: deps.CurrentUser,
    background_tasks: BackgroundTasks,
):
    """
    Submit a new news item from a URL. Logged-in users only.
    The processing is done in the background.
    """
    background_tasks.add_task(
        crud.news.process_url_submission,
        db=db,
        url=str(item_in.url),
        user_id=current_user.id,
    )
    return {
        "message": "News submission received. It will be processed in the background."
    }


@router.put(
    "/{news_item_id}",
    response_model=NewsItemRead,
    dependencies=[Depends(deps.get_current_active_superuser)],
)
async def update_news_item(
    news_item_id: uuid.UUID,
    news_item_in: NewsItemUpdate,
    db: deps.SessionDep,
):
    """
    Update a news item. Superuser only.
    """
    news_item = await crud.news.get(db=db, id=news_item_id)
    if not news_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="News item not found"
        )
    updated_item = await crud.news.update(db=db, db_obj=news_item, obj_in=news_item_in)
    return updated_item


@router.delete(
    "/{news_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(deps.get_current_active_superuser)],
)
async def delete_news_item(
    news_item_id: uuid.UUID,
    db: deps.SessionDep,
):
    """
    Delete a news item. Superuser only.
    """
    news_item = await crud.news.get(db=db, id=news_item_id)
    if not news_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="News item not found"
        )
    await crud.news.remove(db=db, id=news_item_id)


@router.post(
    "/trigger-news-fetcher",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(deps.get_current_active_superuser)],
)
async def trigger_news_fetcher_endpoint(
    db: deps.SessionDep,
    background_tasks: BackgroundTasks,
    force_run: bool = Query(
        False,
        description="Run the fetcher even if the cooldown period has not passed.",
    ),
):
    """
    Triggers the news fetcher background task.
    """
    from app.scripts.run_news_fetcher import run_fetcher

    await run_fetcher(db, background_tasks, force_run)
    return {"message": "News fetcher job has been triggered."}


@router.get(
    "/run-test",
    response_model=str,
    dependencies=[Depends(deps.get_current_active_superuser)],
)
async def run_test_fetcher(db: deps.SessionDep):
    """
    Run the test news fetcher script.
    """
    from app.scripts.test_news_fetcher import main

    result = await main(db)
    return result

@router.post(
    "/force-update",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(deps.get_current_active_superuser)],
)
async def force_news_update(
    db: deps.SessionDep,
    background_tasks: BackgroundTasks,
    current_user: deps.CurrentUser,
):
    """
    Force immediate news update. Superuser only.
    This bypasses the scheduler and runs the news fetching immediately.
    """
    logger.info(f"[API] User {current_user.email} forcing news update")
    
    try:
        from app.services.ated_news_service import fetch_and_store_news
        
        # Ejecutar en background para no bloquear la respuesta
        background_tasks.add_task(fetch_and_store_news, user=current_user)
        
        return {
            "message": "News update started in background",
            "status": "processing",
            "user": current_user.email
        }
    except Exception as e:
        logger.error(f"Error starting news update: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to start news update: {str(e)}"
        )

@router.post(
    "/force-update-now",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(deps.get_current_active_superuser)],
)
async def force_news_update_now(
    db: deps.SessionDep,
    background_tasks: BackgroundTasks,
    current_user: deps.CurrentUser,
):
    """
    Force immediate news update without time check. Superuser only.
    This bypasses the 6-hour check and runs the news fetching immediately.
    """
    logger.info(f"[API] User {current_user.email} forcing immediate news update")
    
    try:
        from app.services.aggregated_news_service import fetch_and_store_news_force
        
        # Ejecutar en background para no bloquear la respuesta
        background_tasks.add_task(fetch_and_store_news_force, user=current_user)
        
        return {
            "message": "Immediate news update started in background",
            "status": "started",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"[API] Error starting force news update: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start news update: {str(e)}"
        )

@router.get(
    "/status",
    dependencies=[Depends(deps.get_current_active_superuser)],
)
async def get_news_status(db: deps.SessionDep):
    """
    Get news system status and statistics. Superuser only.
    """
    try:
        # Obtener estadísticas básicas
        total_news = await crud.news.count(db)
        recent_news = await crud.news.get_recent_news(db, hours=24)
        
        return {
            "total_news_items": total_news,
            "news_last_24h": len(recent_news),
            "last_update": recent_news[0].created_at if recent_news else None,
            "system_status": "operational"
        }
    except Exception as e:
        logger.error(f"Error getting news status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to get news status: {str(e)}"
        )