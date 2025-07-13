import asyncio
import httpx
import logging
from typing import Any, Dict, List
from datetime import datetime, timezone, timedelta
import uuid
import json
import feedparser
import time
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import RetryError
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from rapidfuzz import fuzz
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import re
from bs4 import BeautifulSoup

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
    url = f"https://gnews.io/api/v4/search?q={query_str}&lang=en&max=40&token={settings.GNEWS_API_KEY}"
    
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
        "articlesCount": 50
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

def extract_img_from_description(description: str) -> str | None:
    match = re.search(r'<img[^>]+src="([^"]+)"', description or "")
    if match:
        return match.group(1)
    return None

async def _fetch_from_rss_feed(client: httpx.AsyncClient, feed_url: str) -> List[Dict]:
    """Fetches articles from a given RSS feed URL."""
    logger.info(f"Fetching from RSS feed: {feed_url}")
    try:
        response = await client.get(feed_url, timeout=20.0, follow_redirects=True)
        response.raise_for_status()
        
        parsed_feed = feedparser.parse(response.text)
        source_name = parsed_feed.feed.get("title", feed_url)

        articles = []
        for entry in parsed_feed.entries:
            image_url = None
            # 1. Campos estándar
            if 'media_content' in entry and entry.media_content:
                image_url = entry.media_content[0].get('url')
            elif 'links' in entry:
                for link in entry.links:
                    if link.get('rel') == 'enclosure' and 'image' in link.get('type', ''):
                        image_url = link.get('href')
                        break
            # 2. Imagen en la descripción (HTML)
            if not image_url:
                image_url = extract_img_from_description(entry.get('description', ''))
            # 3. Imagen en content:encoded (si existe)
            if not image_url and 'content' in entry:
                for c in entry.content:
                    image_url = extract_img_from_description(getattr(c, 'value', ''))
                    if image_url:
                        break

            articles.append({
                "title": entry.get("title"),
                "url": entry.get("link"),
                "source": {"name": source_name},
                "publishedAt": entry.get("published") or entry.get("updated"),
                "image": image_url,
                "description": entry.get("summary")
            })
        
        logger.info(f"RSS ({source_name}): Found {len(articles)} articles.")
        return articles
    except httpx.RequestError as e:
        logger.error(f"Error fetching RSS feed {feed_url}: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred when processing RSS feed {feed_url}: {e}")
    return []

async def _fetch_from_hacker_news(client: httpx.AsyncClient, queries: List[str]) -> List[Dict]:
    """Fetches top AI-related stories from Hacker News via Algolia API."""
    # Usar una query más amplia para AI y tecnología
    query_str = "artificial intelligence OR machine learning OR AI OR neural network OR deep learning OR OpenAI OR ChatGPT OR tech"
    url = f"https://hn.algolia.com/api/v1/search?query={query_str}&tags=story&hitsPerPage=50"
    
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

async def extract_image_from_html(url: str) -> str | None:
    try:
        async with httpx.AsyncClient(headers=BROWSER_HEADERS, timeout=10) as client:
            resp = await client.get(url)
            soup = BeautifulSoup(resp.text, "html.parser")
            # 1. Open Graph
            og = soup.find("meta", property="og:image")
            if og and og.get("content"):
                return og["content"]
            # 2. Twitter Card
            tw = soup.find("meta", attrs={"name": "twitter:image"})
            if tw and tw.get("content"):
                return tw["content"]
            # 3. Primera imagen relevante
            for img in soup.find_all("img"):
                src = img.get("src")
                if src and not re.search(r"(logo|icon|sprite|blank|pixel)", src, re.I):
                    return src
    except Exception as e:
        logger.warning(f"Error extracting image from {url}: {e}")
    return None

async def _is_title_too_similar(db: AsyncSession, title: str, threshold: int = 90) -> bool:
    """
    Checks if a given title is too similar to any existing title in the DB.
    """
    query = select(NewsItem.title)
    try:
        result = await db.execute(query)
        existing_titles = result.scalars().all()
        for existing_title in existing_titles:
            similarity_ratio = fuzz.ratio(title.lower(), existing_title.lower())
            if similarity_ratio > threshold:
                logger.info(f"New title '{title}' is {similarity_ratio:.2f}% similar to existing title '{existing_title}'. Skipping.")
                return True
    except Exception as e:
        logger.error(f"Error checking similarity: {e}")
        # En caso de error en la comprobación, es más seguro asumir que no es similar
        # para no bloquear noticias legítimas.
        return False
    return False

def _robust_date_parse(date_input: str | datetime | None) -> datetime:
    """
    Parses a date from various formats into a timezone-aware datetime object.
    Handles ISO 8601 strings, RFC 822 formatted strings, and existing datetime objects.
    """
    if isinstance(date_input, datetime):
        # If it's already a datetime object, just ensure it's timezone-aware
        if date_input.tzinfo is None:
            return date_input.replace(tzinfo=timezone.utc)
        return date_input

    if not isinstance(date_input, str) or not date_input:
        return datetime.now(timezone.utc)

    # Attempt to parse various formats
    try:
        # Try RFC 822 format (e.g., "Wed, 09 Jul 2025 16:50:00 -0400")
        dt = parsedate_to_datetime(date_input)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        pass

    try:
        # Try ISO 8601 format (e.g., "2024-07-11T19:30:00Z")
        if date_input.upper().endswith('Z'):
            dt = datetime.fromisoformat(date_input[:-1] + '+00:00')
        else:
            dt = datetime.fromisoformat(date_input)
        
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        pass
    
    # Fallback if all parsing fails
    logger.warning(f"Could not parse date '{date_input}'. Using current time.")
    return datetime.now(timezone.utc)


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

    # 1. PRE-FILTERING: Basic data validation
    if not all([url, title, source_name]) or not is_valid_url(url) or title == "[Removed]":
        logger.debug(f"Skipping article with missing essential data or invalid URL: {title}")
        return

    # 2. IMAGE URL CHECK: Ensure an image URL is present before any expensive processing
    if not image_url_raw:
        # Intentar extraer imagen del HTML del artículo
        image_url_raw = await extract_image_from_html(url)
        if not image_url_raw:
            logger.info(f"Skipping article with no image URL (even after HTML fallback): {title}")
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
        
        # Si no hay imagen válida, usar una imagen por defecto
        if not final_image_url:
            final_image_url = "https://ivanintech.com/static/default-news.jpg"  # Cambia por tu imagen por defecto
        
        # We add a final check here: if after all validation the image is None, we discard.
        if not final_image_url:
            logger.info(f"Skipping article as no valid image could be confirmed: {title}")
            return
        
        # 3. Create and store the news item
        news_item_data = NewsItemCreate(
            title=title,
            url=url,
            description=article.get("description"),
            imageUrl=final_image_url,
            sourceName=article.get("sourceName"),
            summary=enriched_data.get("summary"),
            submitted_by_user_id=user.id,
            promotion_level=enriched_data.get("promotion_level", "low"),
            is_community=False,  # Marcar como no comunitario por defecto
            publishedAt=article.get("publishedAt")  # Guardar la fecha de publicación
        )

        # 4. Store the news item in the database
        await news.create(db=db, obj_in=news_item_data)
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
            rss_feeds = settings.NEWS_RSS_FEEDS
            
            async with httpx.AsyncClient(headers=BROWSER_HEADERS) as client:
                # Tareas para las APIs existentes
                tasks = [
                    _fetch_from_gnews(client, queries),
                    _fetch_from_event_registry(client, queries),
                    _fetch_from_hacker_news(client, queries)
                ]
                # Añadir tareas para cada feed RSS
                tasks.extend([_fetch_from_rss_feed(client, feed_url) for feed_url in rss_feeds])
                
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

            # Ordena los artículos por fecha de publicación (si existe), los más nuevos primero
            # Como hemos quitado la fecha, esta ordenación ya no es necesaria
            # all_articles.sort(
            #     key=lambda x: _robust_date_parse(x.get("publishedAt")) or datetime.min.replace(tzinfo=timezone.utc),
            #     reverse=True
            # )
            
            logger.info(f"Total unique articles to process: {len(all_articles)}")

            # Procesa los artículos secuencialmente para evitar problemas de concurrencia con la sesión de la BBDD
            for article in all_articles:
                try:
                    await _process_and_store_article(db, article, user, gemini_service)
                except Exception as e:
                    logger.error(f"Failed to process article {article.get('url')}: {e}", exc_info=True)

        except RetryError as e:
            logger.error(f"Gemini service failed after multiple retries: {e}. Aborting cycle.", exc_info=True)
        except Exception as e:
            logger.error(f"An unexpected error occurred during the fetch/store cycle: {e}", exc_info=True)
        finally:
            logger.info("--- Finished news fetching and storing cycle ---")
            await db.close() # Ensure the session is closed.
