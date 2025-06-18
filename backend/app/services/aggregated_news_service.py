import asyncio
import httpx
import logging
from typing import Any, Dict, List
from datetime import datetime, timezone
import uuid
import json

from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import RetryError
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.crud.crud_news import news_item as news
from app.db.models.user import User
from app.schemas.news import NewsItemCreate
from app.services.gemini_service import generate_resource_details
from app.utils import is_valid_url, parse_datetime_flexible

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
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

    query_str = {"$query": {"keyword": {"$or": queries}, "lang": "eng"}}
    url = f"https://eventregistry.org/api/v1/article/getArticles?apiKey={settings.EVENT_REGISTRY_API_KEY}"
    
    try:
        response = await client.post(url, json={"query": query_str, "resultType": "articles", "articlesSortBy": "date", "articlesCount": 20})
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
    except httpx.RequestError as e:
        logger.error(f"Error fetching from Event Registry: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred when fetching from Event Registry: {e}")
    return []

async def _fetch_from_hacker_news(client: httpx.AsyncClient, queries: List[str]) -> List[Dict]:
    """Fetches top AI-related stories from Hacker News via Algolia API."""
    query_str = " OR ".join(queries)
    url = f"https://hn.algolia.com/api/v1/search?query={query_str}&tags=story&hitsPerPage=20"
    
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

async def _process_and_store_article(
    db: AsyncSession, article: Dict[str, Any], user: User
):
    """
    Processes a single article, enriches it with AI, filters it based on quality gates,
    and stores it in the database if it passes.
    """
    url = article.get("url")
    title = article.get("title")
    source_name = article.get("source", {}).get("name")
    image_url_raw = article.get("image") or article.get("urlToImage")

    # 1. PRE-FILTERING: Basic data validation
    if not all([url, title, source_name]) or not is_valid_url(url) or title == "[Removed]":
        logger.debug(f"Skipping article with missing essential data or invalid URL: {title}")
        return

    # New Filter: Skip if there's no image URL from the source
    if not image_url_raw:
        logger.info(f"Skipping article '{title}' with no initial image URL.")
        return

    try:
        # 2. ENRICHMENT: Call Gemini for analysis
        enriched_data = await generate_resource_details(url=url, user_title=title)
        if not enriched_data:
            logger.warning(f"Could not generate details for article: {title}")
            return

        # 3. POST-FILTERING: AI-based quality gates
        is_related = enriched_data.get("is_related_to_ai", False)
        relevance_rating = enriched_data.get("rate_relevance", 0)

        # New Filter: Check if Gemini thinks it's related
        if not is_related:
            logger.info(f"Skipping article not related to AI: '{title}'")
            return

        # New Filter: Check Gemini's rating
        if relevance_rating <= 3:
            logger.info(f"Skipping article with low relevance rating ({relevance_rating}/5): '{title}'")
            return
        
        # 4. DATA PREPARATION & STORAGE
        final_image_url = enriched_data.get("thumbnail_url_suggestion") or image_url_raw
        
        published_at_str = article.get("publishedAt")
        published_at_dt = parse_datetime_flexible(published_at_str)
        if not published_at_dt:
            logger.warning(f"Could not parse date {published_at_str} for article {title}. Skipping.")
            return

        news_item_data = NewsItemCreate(
            id=str(uuid.uuid4()),
            title=enriched_data.get("title", title),
            url=url,
            sourceName=source_name,
            description=enriched_data.get("ai_generated_description", article.get("description")),
            imageUrl=final_image_url,
            publishedAt=published_at_dt,
            sectors=enriched_data.get("tags", []),
            is_community=False,
            relevance_rating=relevance_rating,
        )

        await news.create(
            db, 
            obj_in=news_item_data
        )
        logger.info(f"Successfully stored article: {title}")

    except IntegrityError:
        logger.info(f"Article '{title}' with URL '{url}' already exists. Skipping.")
        await db.rollback() # Rollback the failed transaction
    except ValueError as e:
        logger.warning(f"Skipping article '{title}' due to validation error: {e}")
    except RetryError as e:
        logger.error(f"API Error after retries for article '{title}': {e}")
    except Exception as e:
        logger.error(f"Unexpected error processing article '{title}': {e}", exc_info=True)


async def fetch_and_store_news(db: AsyncSession, user: User):
    """
    Fetches news from various sources, processes them sequentially, and stores them in the database.
    """
    queries = [
        "artificial intelligence", "machine learning", "large language models",
        "AI ethics", "robotics", "neural networks"
    ]
    
    all_articles = []
    async with httpx.AsyncClient(headers=BROWSER_HEADERS, timeout=30.0, follow_redirects=True) as client:
        fetch_tasks = [
            _fetch_from_gnews(client, queries),
            _fetch_from_event_registry(client, queries),
            _fetch_from_hacker_news(client, queries),
        ]
        
        results = await asyncio.gather(*fetch_tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_articles.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"An API call failed during fetch: {result}", exc_info=True)

    # --- Deduplication on fetched articles before processing ---
    # To handle cases where different sources return the same article in one batch
    seen_urls_in_batch = set()
    unique_articles_in_batch = []
    for article in all_articles:
        url = article.get("url")
        if url and url not in seen_urls_in_batch:
            unique_articles_in_batch.append(article)
            seen_urls_in_batch.add(url)
    
    logger.info(f"Total articles fetched: {len(all_articles)}. Processing {len(unique_articles_in_batch)} unique articles from this batch.")
    
    # --- Sequential Processing ---
    processed_count = 0
    for article in unique_articles_in_batch:
        try:
            # Efficiently check if URL exists in DB before detailed processing
            url = article.get("url")
            if not url or not is_valid_url(url):
                continue
            
            existing_item = await news.get_by_url(db, url=url)
            if existing_item:
                logger.info(f"Article with URL '{url}' already in DB. Skipping.")
                continue

            await _process_and_store_article(db, article, user)
            processed_count += 1
            if processed_count < len(unique_articles_in_batch):
                logger.info(f"Processed article {processed_count}/{len(unique_articles_in_batch)}. Waiting 5 seconds...")
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            logger.warning("News fetching task was cancelled. Shutting down gracefully.")
            break # Exit the loop gracefully
        except Exception as e:
            title = article.get("title", "Unknown")
            logger.error(f"Critical error in main loop for article '{title}': {e}", exc_info=True)

    logger.info("News fetching and storing process completed.")
