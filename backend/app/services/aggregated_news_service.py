import asyncio
import httpx
import logging
from typing import Any, Dict, List
from datetime import datetime, timezone, timedelta
import uuid
import json

from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import RetryError
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from rapidfuzz import fuzz

from app.core.config import settings
from app.crud.crud_news import news
from app.db.models.user import User
from app.db.models.news_item import NewsItem
from app.schemas.news import NewsItemCreate
from app.services.gemini_service import GeminiService
from app.utils import is_valid_url, parse_datetime_flexible, is_valid_image_url
from app.db.session import async_session_maker
from app.services.supabase_service import supabase_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/"
}

async def _fetch_from_gnews(client: httpx.AsyncClient, queries: List[str]) -> List[Dict]:
    """Fetches articles from GNews."""
    if not settings.GNEWS_API_KEY:
        logger.warning("GNews API key is not set. Skipping fetch.")
        return []
    
    query_str = ' OR '.join(f'"{q}"' for q in queries)
    url = f"https://gnews.io/api/v4/search?q={query_str}&lang=en&max=10&token={settings.GNEWS_API_KEY}"
    
    try:
        response = await client.get(url, timeout=20.0)
        response.raise_for_status()
        data = response.json()
        articles = data.get('articles', [])
        logger.info(f"GNews: Found {len(articles)} articles.")
        return articles
    except httpx.RequestError as e:
        logger.error(f"Error fetching from GNews: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred when fetching from GNews: {e}")
    return []

async def _fetch_from_event_registry(client: httpx.AsyncClient, queries: List[str]) -> List[Dict]:
    """Fetches articles from Event Registry (NewsAPI.ai)."""
    if not settings.EVENT_REGISTRY_API_KEY:
        logger.warning("Event Registry API key is not set. Skipping fetch.")
        return []

    # The query parameters are now all in the JSON body.
    url = "https://eventregistry.org/api/v1/article/getArticles"
    payload = {
        "apiKey": settings.EVENT_REGISTRY_API_KEY,
        "query": {
            "$query": {
                "keyword": {"$or": queries},
                "lang": "eng"
            }
        },
        "resultType": "articles",
        "articlesSortBy": "date",
        "articlesCount": 20
    }
    
    try:
        # Pass the full payload as the json parameter.
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        articles_data = data.get('articles', {}).get('results', [])
        
        # Adapt the response to our standard format
        formatted_articles = [
            {
                "title": article.get("title"),
                "url": article.get("url"),
                "source": {"name": article.get("source", {}).get("title")},
                "publishedAt": article.get("dateTimePub"),
                "image": article.get("image"),
            }
            for article in articles_data
        ]
        logger.info(f"Event Registry: Found {len(formatted_articles)} articles.")
        return formatted_articles
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP Error fetching from Event Registry: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"Error fetching from Event Registry: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred when fetching from Event Registry: {e}")
    return []

async def _fetch_from_hacker_news(client: httpx.AsyncClient, queries: List[str]) -> List[Dict]:
    """Fetches top AI-related stories from Hacker News via Algolia API."""
    # Usar una query más amplia para AI y tecnología
    query_str = "artificial intelligence OR machine learning OR AI OR neural network OR deep learning OR OpenAI OR ChatGPT OR tech"
    url = f"https://hn.algolia.com/api/v1/search?query={query_str}&tags=story&hitsPerPage=30"
    
    try:
        response = await client.get(url, timeout=20.0)
        response.raise_for_status()
        data = response.json()
        hits = data.get('hits', [])
        
        # Adapt the response to our standard format
        formatted_articles = [
            {
                "title": hit.get("title"),
                "url": hit.get("url"),
                "source": {"name": "Hacker News"},
                "publishedAt": hit.get("created_at"),
            }
            for hit in hits if hit.get("url")
        ]
        logger.info(f"Hacker News: Found {len(formatted_articles)} articles.")
        return formatted_articles
    except httpx.RequestError as e:
        logger.error(f"Error fetching from Hacker News: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred when fetching from Hacker News: {e}")
    return []

async def _is_title_too_similar(db: AsyncSession, new_title: str) -> bool:
    """
    Checks if a new title is too similar to any existing titles from the last 48 hours.
    """
    # 1. Get titles from the last 48 hours to keep the check efficient
    time_threshold = datetime.now(timezone.utc) - timedelta(days=2)
    query = select(NewsItem.title).where(NewsItem.publishedAt >= time_threshold)
    result = await db.execute(query)
    existing_titles = result.scalars().all()

    # 2. Compare the new title against existing ones using rapidfuzz
    for existing_title in existing_titles:
        similarity_ratio = fuzz.ratio(new_title.lower(), existing_title.lower())
        if similarity_ratio > 80:
            logger.info(f"New title '{new_title}' is {similarity_ratio:.2f}% similar to existing title '{existing_title}'. Skipping.")
            return True
            
    return False

async def _process_and_store_article(
    db: AsyncSession, 
    article: Dict[str, Any], 
    user: User,
    gemini_service: GeminiService
):
    """
    Processes a single article, enriches it with AI, filters it based on quality gates,
    and stores it in the database if it passes.
    """
    url = article.get("url")
    title = article.get("title")
    source_name = article.get("source", {}).get("name")
    image_url_raw = article.get("image") or article.get("urlToImage")

    # --- Start of new validation block ---

    # 1. PRE-FILTERING: Basic data validation
    if not all([url, title, source_name]) or not is_valid_url(url) or title == "[Removed]":
        logger.debug(f"Skipping article with missing essential data or invalid URL: {title}")
        return

    # 2. IMAGE URL CHECK: Ensure an image URL is present before any expensive processing
    if not image_url_raw:
        logger.info(f"Skipping article with no image URL: {title}")
        return

    # 3. DUPLICATE CHECK: Check if the article already exists in the DB
    existing_article = await news.get_by_url(db, url=url)
    if existing_article:
        logger.info(f"Skipping duplicate article by URL: {title}")
        return

    # 4. SIMILARITY CHECK: Check if the title is too similar to existing ones
    if await _is_title_too_similar(db, title):
        return
        
    # --- End of validation block ---

    try:
        # 4. ENRICHMENT: Get content and then analyze it (this is the expensive part)
        content = await gemini_service.get_content_from_url(url=url)
        if not content:
            logger.warning(f"Could not get content for article: {title}. Skipping.")
            return

        enriched_data = await gemini_service.evaluate_and_summarize_content(
            title=title,
            content=content
        )

        if not enriched_data:
            logger.warning(f"Could not generate details for article: {title}")
            return
            
        # --- Validation Step ---
        if not enriched_data.get("summary"):
            logger.warning(f"Skipping article due to missing summary: '{title}'")
            return

        # 5. POST-FILTERING: AI-based quality gates
        is_related = enriched_data.get("is_related_to_tech", False)
        relevance_rating = enriched_data.get("relevance_rating", 0.0)

        # New Filter: Check if Gemini thinks it's related
        if not is_related:
            logger.info(f"Skipping article not related to AI/Tech: '{title}'")
            return

        # New Filter: Check Gemini's rating
        if relevance_rating < 2.5:
            logger.info(f"Skipping article with low relevance rating ({relevance_rating}/5): '{title}'")
            return
        
        # New Filter: Check credibility score to avoid "fake news" or low-quality content
        credibility_score = enriched_data.get("credibility_score", 5.0) # Default to high credibility if key is missing
        if credibility_score < 2.5:
            logger.info(f"Skipping article with low credibility score ({credibility_score}/5): '{title}'")
            return

        # 6. DATA PREPARATION & IMAGE VALIDATION
        final_image_url = enriched_data.get("thumbnail_url_suggestion") or image_url_raw

        # --- Image Validation Step ---
        if final_image_url and not await is_valid_image_url(final_image_url):
            logger.info(f"Skipping article due to invalid or too small image: {title} ({final_image_url})")
            final_image_url = None # Set to None if invalid
        
        # We add a final check here: if after all validation the image is None, we discard.
        if not final_image_url:
            logger.info(f"Skipping article as no valid image could be confirmed: {title}")
            return
        
        published_at_str = article.get("publishedAt")
        published_at_dt = parse_datetime_flexible(published_at_str)
        if not published_at_dt:
            logger.warning(f"Could not parse publishedAt '{published_at_str}' for article: {title}. Using current time.")
            published_at_dt = datetime.now(timezone.utc)

        news_item_data = NewsItemCreate(
            title=title,
            url=url,
            description=enriched_data.get("summary"),
            # Ensure URL is a string for Pydantic validation
            imageUrl=str(final_image_url) if final_image_url else None,
            sectors=enriched_data.get("sectors", []),
            publishedAt=published_at_dt,
            sourceName=source_name,
            sourceId=article.get("source", {}).get("id"),
            relevance_rating=relevance_rating
        )

        await news.create_with_owner(db=db, obj_in=news_item_data, user_id=user.id)
        logger.info(f"Successfully stored article: {title}")

    except IntegrityError:
        await db.rollback()
        logger.info(f"Article '{title}' with URL '{url}' already exists. Skipping.")
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to process or store article '{title}': {e}", exc_info=True)


async def fetch_and_store_news(user: User):
    """
    Main orchestrator function that fetches news from all sources,
    processes them, and stores them in the database.
    
    This function is designed to be run as a background task.
    """
    logger.info("--- Starting news fetching and storing cycle ---")

    async with async_session_maker() as db:
        try:
            gemini_service = GeminiService()
            
            queries = settings.NEWS_QUERIES
            
            async with httpx.AsyncClient(headers=BROWSER_HEADERS) as client:
                tasks = [
                    _fetch_from_gnews(client, queries),
                    _fetch_from_event_registry(client, queries),
                    _fetch_from_hacker_news(client, queries)
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)

            all_articles = []
            for result in results:
                if isinstance(result, list):
                    all_articles.extend(result)
                elif isinstance(result, Exception):
                    logger.error(f"Error fetching from a news source: {result}", exc_info=True)

            if not all_articles:
                logger.info("No articles fetched from any source. Ending cycle.")
                return

            # Sort by publication date, newest first. Handle None dates gracefully.
            all_articles.sort(
                key=lambda x: parse_datetime_flexible(x.get("publishedAt")) or datetime.min.replace(tzinfo=timezone.utc),
                reverse=True
            )
            
            logger.info(f"Total unique articles to process: {len(all_articles)}")

            process_tasks = [
                _process_and_store_article(db, article, user, gemini_service)
                for article in all_articles
            ]
            
            await asyncio.gather(*process_tasks)

        except RetryError as e:
            logger.error(f"Gemini service failed after multiple retries: {e}. Aborting cycle.", exc_info=True)
        except Exception as e:
            logger.error(f"An unexpected error occurred during the fetch/store cycle: {e}", exc_info=True)
        finally:
            logger.info("--- Finished news fetching and storing cycle ---")
            await db.close() # Ensure the session is closed.
