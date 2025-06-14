import asyncio
import json
import logging
from typing import List, Optional, cast

import google.generativeai as genai
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func # For func.json_length or similar if needed
from sqlalchemy import JSON

from app.core.config import settings
from app.db.session import AsyncSessionLocal, async_engine # Added async_engine for potential direct use if needed
from app.db.models.news_item import NewsItem # Import NewsItem model
from app.db.base import Base # To create tables if script is run standalone for the first time (optional)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure Gemini API Key
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    logger.info("Gemini API Key configured.")
else:
    logger.warning("GEMINI_API_KEY is not configured. The script will not be able to fetch AI sectors.")

async def get_sectors_from_gemini(title: str, description: Optional[str]) -> List[str]:
    """
    Gets a list of relevant sectors for a news item using Gemini.
    """
    if not settings.GEMINI_API_KEY:
        logger.error("Cannot call Gemini: API key not configured.")
        return []

    model = genai.GenerativeModel("gemini-1.5-flash-latest") # Using the same model as gemini_service

    prompt_parts = [
        "You are an expert assistant in categorizing technology news.",
        "Analyze the following news title and description and return a list of up to 5 key technology sectors to which it belongs.",
        "Common sectors could be: 'Artificial Intelligence', 'Cloud Computing', 'Cybersecurity', 'Software Development', 'Hardware', 'Gaming', 'Mobile', 'Startups', 'eCommerce', 'Fintech', 'EdTech', 'HealthTech', 'Blockchain', 'Tech Sustainability', 'IoT', 'Big Data', 'Virtual/Augmented Reality'.",
        "If you are unsure or it does not apply, return an empty list.",
        "Return ONLY a JSON object that is a list of strings. For example: [\"AI\", \"Cloud\"] or [].",
        "Do not include additional explanations, only the JSON.",
        "---",
        f"Title: {title}",
    ]
    if description:
        prompt_parts.append(f"Description: {description[:1000]}") # Limit description length
    prompt_parts.append("---")
    prompt_parts.append("List of sectors (JSON):")
    
    complete_prompt = "\n".join(prompt_parts)

    try:
        # logger.debug(f"Prompt for Gemini:\n{complete_prompt}")
        response = await model.generate_content_async(complete_prompt)
        
        cleaned_response_text = response.text.strip()
        # logger.debug(f"Gemini response (raw): {cleaned_response_text}")

        if cleaned_response_text.startswith("```json"):
            cleaned_response_text = cleaned_response_text[7:]
        if cleaned_response_text.endswith("```"):
            cleaned_response_text = cleaned_response_text[:-3]
        
        cleaned_response_text = cleaned_response_text.strip() # Ensure no extra spaces
        
        # Attempt to parse. If it is just an empty list '[]', it might not be detected by the ```json```
        if not cleaned_response_text: # If it's empty after cleaning, assume an empty list
             logger.warning(f"Gemini returned an empty response for '{title}'. Assuming [].")
             return []

        sectors = json.loads(cleaned_response_text)
        if isinstance(sectors, list) and all(isinstance(s, str) for s in sectors):
            logger.info(f"Sectors obtained for '{title}': {sectors}")
            return sectors
        else:
            logger.warning(f"Gemini response was not a list of strings for '{title}': {sectors}. Response was: {cleaned_response_text}")
            return []
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from Gemini for '{title}'. Response: \n{response.text}", exc_info=True)
        return []
    except Exception as e:
        logger.error(f"Error calling Gemini API for '{title}': {e}", exc_info=True)
        return []

async def auto_tag_news_sectors(db: AsyncSession, limit: Optional[int] = None):
    """
    Iterates through news items without sectors and assigns them sectors using Gemini.
    """
    logger.info("Starting the auto-tagging process for news sectors.")
    
    # SQLAlchemy doesn't have a simple native JSON list type for SQLite.
    # We use `None` for new items and `cast([], JSON)` for existing empty lists.
    # The `cast([], JSON)` is more for PostgreSQL or MySQL.
    # For SQLite, we might need `NewsItem.sectors.astext == '[]'` or similar, or filter in Python.
    # For now, we focus on `sectors IS NULL` and filtering for `[]` in Python for simplicity.
    # Or better yet, use func.json_type or func.json_array_length if the database supports it (e.g., PostgreSQL).
    # For SQLite, `NewsItem.sectors == json.dumps([])` could work if they are saved as strings.
    # Or `NewsItem.sectors == []` if SQLAlchemy maps it correctly.
    # Since NewsItem.sectors is Mapped[Optional[List[str]]] = mapped_column(JSON..),
    # SQLAlchemy should handle `[]` correctly in comparisons if the dialect supports it.
    # The safest way is NewsItem.sectors == None and then a json_array_length if it's pg, or filter in python.

    stmt = select(NewsItem)

    if limit:
        stmt = stmt.limit(limit)

    result = await db.execute(stmt)
    news_items_to_process = result.scalars().all()
    
    # Additional filtering in Python for `[]` if the SQL query is not robust for all cases
    filtered_items = []
    for item in news_items_to_process:
        if item.sectors is None or item.sectors == []:
            filtered_items.append(item)
    news_items_to_process = filtered_items

    if not news_items_to_process:
        logger.info("No news items found that need sector tagging.")
        return

    logger.info(f"Found {len(news_items_to_process)} news items to process.")
    
    processed_count = 0
    updated_count = 0

    for news_item in news_items_to_process:
        logger.info(f"Processing news ID: {news_item.id}, Title: {news_item.title}")
        
        # Prevent re-processing if it already has sectors (double-check)
        if news_item.sectors and len(news_item.sectors) > 0:
            logger.info(f"Skipping news ID: {news_item.id}, already has sectors: {news_item.sectors}")
            continue

        sectors = await get_sectors_from_gemini(news_item.title, news_item.description)
        
        if sectors: # Only update if Gemini returns something
            news_item.sectors = sectors
            db.add(news_item)
            updated_count += 1
            logger.info(f"News ID: {news_item.id} updated with sectors: {sectors}")
        else:
            # Optional: Mark as processed to avoid retrying indefinitely if Gemini consistently returns nothing.
            # For now, we simply don't update it, and it will be retried next time.
            # Or we can explicitly set an empty list if we want to mark it as "tried but no result".
            # According to the plan, if there are no sectors, an empty list is saved.
            # The get_sectors_from_gemini function already returns [] in case of error or no sectors.
            # So if `sectors` is empty here, it's because Gemini returned [] or there was an error.
            # If we want to save `[]` to indicate "processed, no sectors found", we must do it explicitly.
            # For now, if `sectors` is [], it is not updated (unless it was `None` before).
            # If we want `sectors` to be explicitly `[]` after processing and finding nothing:
            if news_item.sectors is None: # If it was None and Gemini found nothing (returns [])
                news_item.sectors = [] # Set to empty list
                db.add(news_item)
                logger.info(f"News ID: {news_item.id} marked with empty sectors []." )
            else: # If it was already [] and Gemini found nothing, no change.
                logger.info(f"No sectors found for news ID: {news_item.id} or it was already empty.")


        processed_count += 1
        if processed_count % 20 == 0: # Commit every 20 news items
            logger.info(f"Processed {processed_count} news items. Committing partial changes...")
            await db.commit()
            logger.info("Partial commit done.")

        # >>> ADD DELAY HERE <<<
        if settings.GEMINI_API_KEY: # Only pause if we are using the API
            logger.debug(f"Waiting 5 seconds before the next request to Gemini...")
            await asyncio.sleep(5) # 5-second pause

    if processed_count > 0 : # Final commit if anything was processed
        logger.info("Process finished. Making final commit...")
        await db.commit()
        logger.info(f"Final commit done. Total news processed: {processed_count}. Total news updated with new sectors: {updated_count}.")
    else:
        logger.info("No news items were processed in this run.")


async def main(run_limit: Optional[int] = None):
    """
    Main function to run the script.
    """
    # Optional: Create tables if they don't exist (usually handled by Alembic, but useful for standalone scripts)
    # async with async_engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    #     logger.info("Tables (if they didn't exist) verified/created.")

    async with AsyncSessionLocal() as session:
        await auto_tag_news_sectors(session, limit=run_limit)

if __name__ == "__main__":
    # Allow passing a limit from the command line, e.g., python auto_tag_news_sectors.py 10
    limit_arg = None
    import sys
    if len(sys.argv) > 1:
        try:
            limit_arg = int(sys.argv[1])
            logger.info(f"Running script with a limit of {limit_arg} news items.")
        except ValueError:
            logger.warning(f"Argument '{sys.argv[1]}' is not a valid number for the limit. Running without limit.")
            
    asyncio.run(main(run_limit=limit_arg))