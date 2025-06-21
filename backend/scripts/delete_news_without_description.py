import asyncio
import os
import sys
from sqlalchemy import select, delete
from typing import List
from dotenv import load_dotenv

# Adjust the Python path to include the project root (`backend`)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
load_dotenv(os.path.join(project_root, '.env'))

from app.db.session import AsyncSessionLocal
from app.db.models.news_item import NewsItem
from app.utils import is_valid_image_url

async def cleanup_invalid_image_news():
    """
    Connects to the database and deletes news items that have an invalid or low-quality image URL.
    """
    print("Starting cleanup: Deleting news items with invalid images...")
    
    ids_to_delete = set()

    async with AsyncSessionLocal() as db:
        try:
            # 1. Fetch all news items that have an image URL
            stmt = select(NewsItem.id, NewsItem.imageUrl).where(NewsItem.imageUrl.isnot(None))
            result = await db.execute(stmt)
            all_news_with_images = result.all()
            
            print(f"Found {len(all_news_with_images)} news items with an image to validate.")

            # 2. Validate each image URL
            for item_id, image_url in all_news_with_images:
                if not await is_valid_image_url(image_url):
                    print(f"Flagging for deletion: Invalid image '{image_url}' for item {item_id}")
                    ids_to_delete.add(item_id)

            # 3. Perform the deletion
            if not ids_to_delete:
                print("No news items with invalid images found. Database is clean.")
                return

            print(f"Found {len(ids_to_delete)} items to delete.")
            
            delete_statement = delete(NewsItem).where(NewsItem.id.in_(list(ids_to_delete)))
            
            result = await db.execute(delete_statement)
            await db.commit()

            print(f"Successfully deleted {result.rowcount} news item(s).")
            print("Cleanup process finished.")

        except Exception as e:
            await db.rollback()
            print(f"An error occurred: {e}", exc_info=True)
            print("Transaction has been rolled back.")

if __name__ == "__main__":
    asyncio.run(cleanup_invalid_image_news()) 