# ivanintech/backend/app/services/aggregated_news_service.py

import asyncio
import json
import httpx
import google.generativeai as genai
import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError # Import for error handling
from datetime import datetime, timedelta, timezone, date # Add date
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse # To validate URLs
from bs4 import BeautifulSoup
import logging # Add logging
from sqlalchemy import delete
from google.api_core.exceptions import ResourceExhausted
import argparse
import os
import sys
from contextlib import asynccontextmanager
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.schemas.news import NewsItemCreate
from app.services.gemini_service import generate_resource_details
from app import crud  # Import the central crud module
from app.db.models.news_item import NewsItem
from sqlalchemy.future import select
from app.utils import is_valid_url, parse_datetime_flexible

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Headers to mimic a real browser request, preventing 403 errors
BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/"
}

# Asynchronous HTTP client with browser-like headers
# We define it here to be reused by scraping functions
http_client = httpx.AsyncClient(headers=BROWSER_HEADERS, timeout=30.0, follow_redirects=True)

# Constants for APIs (make sure they are in config.py or .env)
NEWSAPI_API_KEY = settings.NEWSAPI_API_KEY
GNEWS_API_KEY = settings.GNEWS_API_KEY
CURRENTS_API_KEY = settings.CURRENTS_API_KEY
MEDIASTACK_API_KEY = settings.MEDIASTACK_API_KEY
# APITUBE_API_KEY = settings.APITUBE_API_KEY # Commented out if not used

# --- Helper Functions --- #

def is_valid_url(url: Optional[str]) -> bool:
    """Check if the URL is valid and uses http or https scheme."""
    if not url:
        return False
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except ValueError:
        return False

def parse_datetime_flexible(date_str: Optional[str]) -> Optional[datetime]:
    """Tries to parse dates in several common ISO formats, returning None if it fails."""
    if not date_str:
        return None
    # Common formats to try
    formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",  # With milliseconds and Z
        "%Y-%m-%dT%H:%M:%SZ",    # Without milliseconds and Z
        "%Y-%m-%d %H:%M:%S",     # Currents API format
        "%Y-%m-%dT%H:%M:%S",     # ISO without offset
        "%Y-%m-%dT%H:%M:%S%z",   # ISO with offset +/-HHMM
        "%Y-%m-%dT%H:%M:%S%Z",   # ISO with timezone name (less reliable)
    ]
    # Try to parse with UTC timezone if possible
    try:
        # Replace 'Z' if it exists
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        # If it has no timezone, we assume UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        # Try with explicit formats if fromisoformat fails
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                 # If it has no timezone, we assume UTC
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                continue
    logger.warning(f"Could not parse date: {date_str}")
    return None # Return None if no format works

# --- Scraping Functions ---

async def scrape_towards_data_science(http_client: httpx.AsyncClient) -> List[Dict[str, str]]:
    """Scrapes the latest articles from Towards Data Science."""
    # This URL is the final, correct destination after redirects.
    url = "https://towardsdatascience.com/latest/"
    articles_found = []
    source_name = "Towards Data Science"

    try:
        logging.info(f"Scraping {source_name} from URL: {url}")
        response = await http_client.get(url, timeout=20.0) 
        response.raise_for_status() # Raise exception for 4xx/5xx HTTP errors

        soup = BeautifulSoup(response.text, 'html.parser')
        limit = 10 
        count = 0
        main_content = soup.find('div', role='main')
        if not main_content:
             logger.warning("No main content found on Towards Data Science.")
             return []
        possible_article_links = main_content.find_all('a', href=True)
        processed_urls = set()
        for link in possible_article_links:
            href = link['href']
            if href.startswith('/') and not href.startswith('//') and len(href) > 50:
                full_url = f"https://towardsdatascience.com{href}"
                if full_url not in processed_urls and '/@' not in full_url and '/m/' not in full_url:
                    title_element = link.find(['h1', 'h2', 'h3', 'h4'])
                    title = title_element.text.strip() if title_element else link.text.strip()
                    if title and len(title) > 10 and "member only" not in title.lower(): 
                        articles_found.append({"title": title, "url": full_url, "sourceName": source_name})
                        processed_urls.add(full_url)
                        count += 1
                        if count >= limit:
                            break
        if not articles_found:
            logger.warning("No article links found matching the pattern on Towards Data Science.")
        logger.info(f"Scraped {len(articles_found)} potential articles from Towards Data Science.")
        return articles_found
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error scraping Towards Data Science: {e.response.status_code} - {e.request.url}")
    except httpx.RequestError as e:
        logger.error(f"Network error scraping Towards Data Science: {e}")
    except Exception as e:
        logger.error(f"Error parsing Towards Data Science page: {e}", exc_info=True)
    return []

# --- External API Functions (Simplified) ---

async def fetch_news_from_newsapi(http_client: httpx.AsyncClient, query: str, page_size: int = 20) -> List[Dict]:
    if not settings.NEWSAPI_API_KEY: return []
    url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&pageSize={page_size}&apiKey={settings.NEWSAPI_API_KEY}"
    try:
        response = await http_client.get(url, timeout=15.0)
        response.raise_for_status()
        data = response.json()
        logger.info(f"NewsAPI: Found {data.get('totalResults', 0)} articles for query '{query}'")
        return data.get('articles', [])
    except Exception as e:
        logger.error(f"Error fetching from NewsAPI: {e}")
        return []

async def fetch_news_from_gnews(http_client: httpx.AsyncClient, query: str, max_results: int = 10) -> List[Dict]:
    if not settings.GNEWS_API_KEY: return []
    url = f"https://gnews.io/api/v4/search?q={query}&lang=en&max={max_results}&token={settings.GNEWS_API_KEY}"
    try:
        response = await http_client.get(url, timeout=15.0)
        response.raise_for_status()
        data = response.json()
        logger.info(f"GNews: Found {data.get('totalArticles', 0)} articles for query '{query}'")
        return data.get('articles', [])
    except Exception as e:
        logger.error(f"Error fetching from GNews: {e}")
        return []

async def fetch_news_from_mediastack(http_client: httpx.AsyncClient, query: str, limit: int = 10) -> List[Dict]:
     if not settings.MEDIASTACK_API_KEY: return []
     url = f"http://api.mediastack.com/v1/news?access_key={settings.MEDIASTACK_API_KEY}&keywords={query}&languages=en&limit={limit}&sort=published_desc"
     try:
         response = await http_client.get(url, timeout=15.0)
         response.raise_for_status()
         data = response.json()
         logger.info(f"Mediastack: Found {len(data.get('data', []))} articles for query '{query}'")
         return data.get('data', [])
     except Exception as e:
         logger.error(f"Error fetching from Mediastack: {e}")
         return []

# --- Analysis Functions --- #
# These functions are now imported from gemini_service.py and removed from here.

async def delete_old_news(db: AsyncSession):
    """Deletes old news items (older than 30 days) using the provided session."""
    one_month_ago = datetime.now(timezone.utc) - timedelta(days=30)
    stmt = delete(NewsItem).where(
        NewsItem.is_community == False,
        NewsItem.publishedAt < one_month_ago
    )
    try:
        result = await db.execute(stmt)
        await db.commit()
        logger.info(f"Successfully deleted {result.rowcount} news items older than one month.")
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting old news: {e}", exc_info=True)

# --- Main Service Function ---

@asynccontextmanager
async def get_db_session() -> AsyncSession:
    """Provide a transactional scope for the main execution."""
    async with AsyncSessionLocal() as session:
        yield session

async def fetch_and_store_news():
    """
    Main function to fetch news from all sources and store them.
    It manages its own database session, suitable for background execution.
    """
    logger.info("Starting the news fetching and storing process...")

    async with get_db_session() as db:
        # 1. Clean up old news first.
        await delete_old_news(db)

        # 2. Fetch all articles from all sources
        queries = ["artificial intelligence", "machine learning", "large language models", "python programming"]
        logger.info(f"Fetching news for queries: {queries}")
        
        async with httpx.AsyncClient(timeout=20.0, headers=BROWSER_HEADERS) as http_client:
            tasks = [fetch_news_from_newsapi(http_client, q) for q in queries]
            tasks.extend([fetch_news_from_gnews(http_client, q) for q in queries])
            tasks.extend([fetch_news_from_mediastack(http_client, q) for q in queries])
            tasks.append(scrape_towards_data_science(http_client))

            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_articles = []
        for result in results:
            if isinstance(result, list):
                all_articles.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"An API call failed during fetch: {result}", exc_info=True)
        
        logger.info(f"Total articles fetched: {len(all_articles)}. Processing {len(set(article['url'] for article in all_articles if 'url' in article))} unique URLs.")

        processed_urls = set()
        new_items_count = 0
        
        # --- Simplified Processing and Storing Logic ---
        for article in all_articles:
            url = article.get("url")
            title = article.get("title")

            if not url or not title or not is_valid_url(url) or url in processed_urls:
                continue
            
            processed_urls.add(url)

            # Check if the news item already exists in the database
            existing_item = await crud.news_item.get_by_url(db, url=url)
            if existing_item:
                logger.debug(f"Skipping existing article: {title}")
                continue

            logger.info(f"Processing new article: {title}")
            
            try:
                # Enrich with Gemini (if applicable)
                enriched_details = await enrich_article_with_gemini(url, title)
                if not enriched_details:
                    continue

                # Prepare the final data for insertion
                news_item_data = NewsItemCreate(
                    title=enriched_details.get("title", title),
                    url=url,
                    description=enriched_details.get("description"),
                    content=enriched_details.get("content"), # Assuming enrichment provides this
                    sourceName=enriched_details.get("sourceName", article.get("source", {}).get("name", "Unknown")),
                    imageUrl=enriched_details.get("imageUrl"),
                    publishedAt=parse_datetime_flexible(article.get("publishedAt") or article.get("published_date")),
                    relevance_score=enriched_details.get("relevance_score"),
                    sentiment=enriched_details.get("sentiment"),
                    sectors=enriched_details.get("sectors"),
                )

                await crud.news_item.create(db, obj_in=news_item_data)
                new_items_count += 1
                logger.info(f"Successfully stored article: {news_item_data.title}")

            except Exception as e:
                logger.error(f"Failed to process or store article '{title}': {e}", exc_info=True)
            
            # --- RATE LIMITING ---
            # Wait for a few seconds before processing the next article to avoid hitting API rate limits.
            finally:
                logger.debug("Waiting for 5 seconds to respect API rate limits...")
                await asyncio.sleep(5)

    logger.info(f"News fetching and storing process completed. Added {new_items_count} new items.")

async def enrich_article_with_gemini(url: str, title: str) -> Optional[Dict[str, Any]]:
    """Enriches a single article with details from Gemini, handling specific errors."""
    if not is_valid_url(url):
        logger.warning(f"Skipping enrichment for invalid URL: {url}")
        return None

    try:
        # Pause to avoid hitting API rate limits
        await asyncio.sleep(5) 
        
        details = await generate_resource_details(url=url, user_title=title)
        return details
    except ValueError as e:
        # This is an expected outcome if Gemini rejects the article as irrelevant.
        logger.info(f"Skipping article '{title}' because it was deemed irrelevant by the validation service: {e}")
        return None
    except ResourceExhausted as e:
        logger.error(f"Gemini API resource exhausted for article '{title}'. The service might be temporarily unavailable or limits exceeded. {e}", exc_info=True)
        # We stop here because continuing will likely result in the same error.
        raise  # Re-raise the exception to stop the main processing loop.
    except Exception as e:
        # This catches other unexpected errors (network issues, other API errors, etc.)
        logger.error(f"An unexpected error occurred while enriching '{title}' with Gemini: {e}", exc_info=True)
        return None # Skip this article but continue with others.

async def cleanup_duplicate_news():
    """Encuentra y elimina noticias duplicadas basándose en el título, conservando la más antigua."""
    async with get_db_session() as db:
        try:
            logger.info("--- [DB ADMIN] Iniciando limpieza de noticias duplicadas...")
            
            all_news_stmt = select(NewsItem).order_by(NewsItem.title, NewsItem.publishedAt.asc())
            result = await db.execute(all_news_stmt)
            all_news = result.scalars().all()

            articles_to_delete_ids = []
            seen_titles = set()
            
            logger.info(f"--- [DB ADMIN] Comprobando {len(all_news)} noticias en total.")

            for item in all_news:
                if item.title in seen_titles:
                    articles_to_delete_ids.append(item.id)
                else:
                    seen_titles.add(item.title)
            
            if not articles_to_delete_ids:
                logger.info("--- [DB ADMIN] No se encontraron noticias duplicadas.")
                return

            logger.info(f"--- [DB ADMIN] Se encontraron {len(articles_to_delete_ids)} artículos duplicados para eliminar.")
            
            delete_stmt = delete(NewsItem).where(NewsItem.id.in_(articles_to_delete_ids))
            delete_result = await db.execute(delete_stmt)
            await db.commit()
            
            logger.info(f"--- [DB ADMIN] Se eliminaron con éxito {delete_result.rowcount} noticias duplicadas.")

        except Exception as e:
            logger.error(f"--- [DB ADMIN] Error durante la limpieza de duplicados: {e}", exc_info=True)
            await db.rollback()

if __name__ == "__main__":
    import argparse

    async def main_cli():
        """Función principal para ejecutar el servicio desde la línea de comandos."""
        parser = argparse.ArgumentParser(description="Servicio de agregación y procesamiento de noticias.")
        parser.add_argument(
            '--task', 
            type=str, 
            choices=['fetch', 'cleanup-duplicates'], 
            required=True,
            help="La tarea a realizar: 'fetch' para obtener noticias o 'cleanup-duplicates' para eliminar duplicados."
        )
        args = parser.parse_args()

        logger.info(f"--- [MAIN] Tarea seleccionada: {args.task} ---")
        
        if args.task == 'fetch':
            await fetch_and_store_news()
        elif args.task == 'cleanup-duplicates':
            await cleanup_duplicate_news()

    logger.info(f"--- [MAIN] Iniciando script. PROJECT_NAME: {settings.PROJECT_NAME} ---")
    asyncio.run(main_cli())