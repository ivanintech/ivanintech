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
from app.db.models.resource_link import ResourceLink

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def populate_star_ratings():
    """
    Finds all resource links and updates their star_rating
    with a random integer value skewed towards higher values.
    """
    logger.info("--- [START] Starting star_rating population script for Resource Links ---")
    session = AsyncSessionLocal()
    try:
        # Step 1: Find all resource links
        stmt = select(ResourceLink)
        result = await session.execute(stmt)
        all_resource_links = result.scalars().all()

        if not all_resource_links:
            logger.info("No resource links found in the database. Exiting.")
            return

        logger.info(f"Found {len(all_resource_links)} resource links to update with new random ratings.")

        # Step 2: Iterate and assign a new random rating to each item
        updated_count = 0
        for item in all_resource_links:
            # Generate a random integer rating, skewed towards 4 and 5.
            # Weights: 1, 2, 3 have low probability. 4, 5 have high probability.
            random_rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 20, 40, 25], k=1)[0]
            item.star_rating = random_rating
            updated_count += 1
        
        logger.info(f"Generated new random ratings for {updated_count} items. Committing to database...")

        # Step 3: Commit all the changes at once
        await session.commit()
        logger.info(f"--- [SUCCESS] Successfully updated {updated_count} resource links. ---")

    except Exception as e:
        logger.error(f"An error occurred during the rating population: {e}", exc_info=True)
        await session.rollback()
    finally:
        await session.close()
        logger.info("--- [END] Database session closed. ---")


if __name__ == "__main__":
    asyncio.run(populate_star_ratings()) 