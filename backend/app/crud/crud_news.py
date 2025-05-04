from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc, asc
from typing import List, Optional, Sequence
from datetime import datetime, timezone, timedelta
import logging

from app.db.models.news_item import NewsItem
from app.schemas.news import NewsItemCreate, NewsItemUpdate

logger = logging.getLogger(__name__)

async def get_news_item(db: AsyncSession, news_item_id: int) -> Optional[NewsItem]:
    return await db.get(NewsItem, news_item_id)

async def get_news_items(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    sort_by: str = "published_date",
    sort_order: str = "desc",
    min_published_date: Optional[datetime] = None
) -> Sequence[NewsItem]:
    """Retrieve news items, ordered by relevance (if available) and date."""
    logger.info(f"[CRUD] Entrando en get_news_items. skip={skip}, limit={limit}, sort_by={sort_by}, sort_order={sort_order}, min_published_date={min_published_date}")
    stmt = select(NewsItem)
    
    if min_published_date:
        if min_published_date.tzinfo is None:
            min_published_date = min_published_date.replace(tzinfo=timezone.utc)
        stmt = stmt.where(NewsItem.publishedAt >= min_published_date)

    sort_column = getattr(NewsItem, sort_by, NewsItem.publishedAt)
    order_func = desc if sort_order.lower() == "desc" else asc
    stmt = stmt.order_by(order_func(sort_column))
    
    stmt = stmt.offset(skip).limit(limit)
    
    logger.info(f"[CRUD] Ejecutando consulta: {str(stmt.compile(compile_kwargs={'literal_binds': True}))}")
    
    result = await db.execute(stmt)
    news_list = result.scalars().all()
    logger.info(f"[CRUD] Consulta completada. Noticias encontradas: {len(news_list)}")
    return news_list

async def get_news_item_by_url(db: AsyncSession, url: str) -> Optional[NewsItem]:
    """Check if a news item with the given URL already exists."""
    stmt = select(NewsItem).filter(NewsItem.url == url)
    result = await db.execute(stmt)
    return result.scalars().first()

async def create_news_item(db: AsyncSession, *, news_item_in: NewsItemCreate) -> NewsItem:
    """Create a new news item in the database."""
    db_news_item = NewsItem(**news_item_in.dict())
    db.add(db_news_item)
    await db.commit()
    await db.refresh(db_news_item)
    return db_news_item

async def create_multiple_news_items(db: AsyncSession, *, news_items_in: List[NewsItemCreate]) -> List[NewsItem]:
    db_news_items = [NewsItem(**item.dict()) for item in news_items_in]
    db.add_all(db_news_items)
    await db.commit()
    # Note: Refreshing multiple items added via add_all might require individual refreshes or re-fetching.
    # For simplicity, we return the input objects augmented potentially by DB defaults if needed elsewhere.
    # If IDs or server-set defaults are strictly needed back, a fetch after commit is safer.
    return db_news_items # Returning instances before potential refresh

async def update_news_item(db: AsyncSession, *, db_news_item: NewsItem, news_item_in: NewsItemUpdate) -> NewsItem:
    update_data = news_item_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_news_item, field, value)
    db.add(db_news_item)
    await db.commit()
    await db.refresh(db_news_item)
    return db_news_item

async def delete_news_item(db: AsyncSession, *, db_news_item: NewsItem):
    await db.delete(db_news_item)
    await db.commit()

# --- Funciones Create, Update, Delete --- 
# ... 