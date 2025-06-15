from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from sqlalchemy import func, text
from sqlalchemy.dialects.postgresql import array_agg

from app.schemas.news import NewsItemCreate, NewsItemUpdate
from app.db.models import NewsItem

async def get_top_sectors(db: AsyncSession, limit: int = 10) -> list[str]:
    """
    Gets the most frequent sectors from all news items using PostgreSQL functions.
    """
    # Unnest the sectors array, count occurrences, and get the top N
    sector_subquery = func.jsonb_array_elements_text(NewsItem.sectors).alias("sector")
    stmt = (
        select(sector_subquery)
        .group_by(sector_subquery)
        .order_by(func.count().desc())
        .limit(limit)
    )
    
    result = await db.execute(stmt)
    top_sectors = result.scalars().all()
    
    return top_sectors

async def get_news_items(db: AsyncSession, skip: int = 0, limit: int = 100, start_date: datetime | None = None) -> list[NewsItem]:
    query = select(NewsItem)
    if start_date:
        query = query.where(NewsItem.publishedAt >= start_date)
    query = query.order_by(NewsItem.publishedAt.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_news_item_by_url(db: AsyncSession, url: str) -> NewsItem | None:
    """Gets a news item by its original source URL."""
    result = await db.execute(select(NewsItem).where(NewsItem.url == url))
    return result.scalars().first()

async def create_news_item(db: AsyncSession, news_item: NewsItemCreate) -> NewsItem:
    """
    Creates a new NewsItem object, adds it to the session, and flushes.
    The calling function is responsible for the commit.
    """
    published_at = news_item.publishedAt if news_item.publishedAt else datetime.utcnow()
    
    db_news_item = NewsItem(
        title=news_item.title,
        description=news_item.description,
        url=str(news_item.url),
        imageUrl=str(news_item.imageUrl) if news_item.imageUrl else None,
        publishedAt=published_at,
        sourceName=news_item.sourceName,
        sourceId=news_item.sourceId,
        relevance_score=news_item.relevance_score,
        sectors=news_item.sectors,
        star_rating=news_item.star_rating,
        is_community=news_item.is_community if news_item.is_community is not None else False,
        # reasoning=news_item.reasoning, # Does not exist in model
        # is_published=news_item.is_published, # Does not exist in model
        # is_current_week_news=news_item.is_current_week_news, # Does not exist in model
        # content=news_item.content, # Does not exist in model
        # author=news_item.author, # Does not exist in model
        # tags=news_item.tags # Does not exist in model
    )
    db.add(db_news_item)
    await db.flush()  # Make the object available in the session without committing
    return db_news_item

# ... (rest of the file: update, delete, etc., if they exist) ...