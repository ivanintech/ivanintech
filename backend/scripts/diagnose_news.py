import asyncio
import logging
import sys
import os

# Add the parent directory to sys.path to allow imports from app
# We need to add 'backend' directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import async_session_maker
from app.db.models.news_item import NewsItem
from sqlalchemy import select, func, desc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def diagnose_news():
    logger.info("Starting News Diagnosis...")
    
    async with async_session_maker() as db:
        try:
            # 1. Check Total Count
            count_stmt = select(func.count(NewsItem.id))
            total = (await db.execute(count_stmt)).scalar_one_or_none() or 0
            logger.info(f"Total News Items in DB: {total}")
            
            if total == 0:
                logger.warning("Database is empty! News ingestion is likely failing or hasn't run.")
                return

            # 2. Check Recent Items
            stmt = select(NewsItem).order_by(desc(NewsItem.publishedAt)).limit(5)
            result = await db.execute(stmt)
            items = result.scalars().all()
            
            logger.info("\n--- Top 5 Most Recent News Items ---")
            for item in items:
                logger.info(f"ID: {item.id}")
                logger.info(f"Title: {item.title}")
                logger.info(f"PublishedAt: {item.publishedAt}")
                logger.info(f"Source: {item.sourceName}")
                logger.info(f"Relevance Rating: {item.relevance_rating}")
                logger.info("-" * 30)

            # 3. Check for NULL publishedAt
            null_date_stmt = select(func.count(NewsItem.id)).where(NewsItem.publishedAt == None)
            null_date_count = (await db.execute(null_date_stmt)).scalar_one_or_none() or 0
            logger.info(f"\nNews Items with NULL publishedAt: {null_date_count}")

        except Exception as e:
            logger.error(f"Error during diagnosis: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(diagnose_news())
