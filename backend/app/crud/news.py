from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select # Ensure select is also imported

from app.schemas.news import NewsItemCreate, NewsItemUpdate # Ensure we have the correct schemas
from datetime import datetime, timedelta # Necessary for date queries
# Import the NewsItem model for CRUD functions
from app.db.models import NewsItem


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
    # Ensure publishedAt has a default value if it's not provided
    published_at = news_item.publishedAt if news_item.publishedAt else datetime.utcnow()
    
    db_news_item = NewsItem(
        title=news_item.title,
        description=news_item.description,
        url=str(news_item.url), # Ensure URL is a string
        imageUrl=str(news_item.imageUrl) if news_item.imageUrl else None, # Ensure image URL is a string or None
        publishedAt=published_at,
        sourceName=news_item.sourceName,
        sourceId=news_item.sourceId,
        relevance_score=news_item.relevance_score,
        sectors=news_item.sectors,
        # id is generated automatically if it's a UUID/GUID or an Integer with autoincrement
    )
    db.add(db_news_item)
    await db.commit()
    await db.refresh(db_news_item)
    return db_news_item

# ... (rest of the file: update, delete, etc., if they exist) ...