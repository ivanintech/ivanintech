import asyncio
import logging
import os
import sys
import random

# --- Adjust path to allow app imports ---
# This allows the script to be run from the project root.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.models.news_item import NewsItem

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def populate_relevance_ratings():
    """
    Finds all news items and updates their relevance_rating
    with a random float value skewed towards higher values.
    """
    logger.info("--- [START] Starting relevance_rating population script ---")
    session = AsyncSessionLocal()
    try:
        # Step 1: Find all news items
        stmt = select(NewsItem)
        result = await session.execute(stmt)
        all_news_items = result.scalars().all()

        if not all_news_items:
            logger.info("No news items found in the database. Exiting.")
            return

        logger.info(f"Found {len(all_news_items)} news items to update with new random ratings.")

        # Step 2: Iterate and assign a new random rating to each item
        updated_count = 0
        for item in all_news_items:
            # Generate a random rating using a triangular distribution.
            # This skews the results towards the 'mode' value (4.0).
            # Range: [1.5, 4.8], Most likely value: 4.0
            random_rating = round(random.triangular(1.5, 4.8, 4.0), 2)
            item.relevance_rating = random_rating
            updated_count += 1
        
        logger.info(f"Generated new random ratings for {updated_count} items. Committing to database...")

        # Step 3: Commit all the changes at once
        await session.commit()
        logger.info(f"--- [SUCCESS] Successfully updated {updated_count} news items. ---")

    except Exception as e:
        logger.error(f"An error occurred during the rating population: {e}", exc_info=True)
        await session.rollback()
    finally:
        await session.close()
        logger.info("--- [END] Database session closed. ---")


if __name__ == "__main__":
    asyncio.run(populate_relevance_ratings()) 