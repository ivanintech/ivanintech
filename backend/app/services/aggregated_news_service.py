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

from app.core.config import settings
# We import the create_news_item function directly from crud_news
# instead of the whole module, to avoid confusion with other crud functions.
# No longer necessary, we will create the objects directly here.
# from app.crud.crud_news import create_news_item 
from app.schemas.news import NewsItemCreate # Schema to create/validate
from app.db.models import NewsItem # Model to query existing URLs
from sqlalchemy.future import select
from app.db.session import AsyncSessionLocal # Import AsyncSessionLocal directly
from app.crud.news import get_news_item_by_url, create_news_item # Import functions directly
from app.services.gemini_service import generate_resource_details, get_sectors_from_gemini # Assuming this service exists

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    logger.info("Gemini API Key configured.")
else:
    logger.warning("GEMINI_API_KEY is not configured. News analysis will not work.")

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
    url = "https://towardsdatascience.com/archive"
    articles_found = []
    source_name = "Towards Data Science"

    try:
        logging.info(f"Scraping {source_name} from URL: {url}")
        response = await http_client.get(url, timeout=20.0) 
        response.raise_for_status() # Raise exception for 4xx/5xx HTTP errors

        soup = BeautifulSoup(response.text, 'html.parser')

        # --- Scraping Logic (THIS IS AN EXAMPLE AND NEEDS ADJUSTMENT!!) ---
        # Inspect the actual TDS website to find the correct selectors.
        # You might need to search for containers, then 'a' elements with 'href', etc.
        # Hypothetical example:
        # article_elements = soup.find_all('div', class_='postArticle') # Adjust selector
        # Simple limiter to avoid processing too many articles
        limit = 10 
        count = 0

        # More realistic example based on the common structure of Medium/TDS:
        # Search for main sections, then articles within them.
        main_content = soup.find('div', role='main')
        if not main_content:
             logger.warning("No main content found on Towards Data Science.")
             return []

        # Try to find articles (this can vary a lot)
        possible_article_links = main_content.find_all('a', href=True)

        processed_urls = set() # To avoid duplicates from the same page

        for link in possible_article_links:
            href = link['href']
            # Filter internal navigation links, profiles, etc., and ensure full URL
            if href.startswith('/') and not href.startswith('//') and len(href) > 50: # Simple heuristic, to be improved
                full_url = f"https://towardsdatascience.com{href}"
                 # Avoid already processed URLs and URLs that don't look like articles
                if full_url not in processed_urls and '/@' not in full_url and '/m/' not in full_url:
                    # Try to get the title from the link text or a nearby h-tag
                    title_element = link.find(['h1', 'h2', 'h3', 'h4'])
                    title = title_element.text.strip() if title_element else link.text.strip()

                    # Accept only if it seems to have a reasonable title
                    if title and len(title) > 10 and "member only" not in title.lower(): 
                        articles_found.append({"title": title, "url": full_url})
                        processed_urls.add(full_url)
                        count += 1
                        if count >= limit:
                            break # Exit if we reach the limit

        # --- End of Example Scraping Logic ---
        if not articles_found:
            logger.warning("No article links found matching the pattern on Towards Data Science.")

        logger.info(f"Scraped {len(articles_found)} potential articles from Towards Data Science.")
        return articles_found

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error scraping Towards Data Science: {e.response.status_code} - {e.request.url}")
    except httpx.RequestError as e:
        logger.error(f"Network error scraping Towards Data Science: {e}")
    except Exception as e:
        logger.error(f"Error parsing Towards Data Science page: {e}", exc_info=True) # Full error log

    return [] # Return empty list in case of error

# --- External API Functions (Simplified) ---

async def fetch_news_from_newsapi(http_client: httpx.AsyncClient, query: str, page_size: int = 20) -> List[Dict]:
    # ... (keep existing logic, ensuring to handle errors and return []) ...
    if not NEWSAPI_API_KEY: return []
    url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&pageSize={page_size}&apiKey={NEWSAPI_API_KEY}"
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
    # ... (keep existing logic, ensuring to handle errors and return []) ...
    if not GNEWS_API_KEY: return []
    url = f"https://gnews.io/api/v4/search?q={query}&lang=en&max={max_results}&token={GNEWS_API_KEY}"
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
     # ... (keep existing logic, ensuring to handle errors and return []) ...
     if not MEDIASTACK_API_KEY: return []
     # Note: Mediastack may require 'keywords' instead of 'q' and has different parameters
     url = f"http://api.mediastack.com/v1/news?access_key={MEDIASTACK_API_KEY}&keywords={query}&languages=en&limit={limit}&sort=published_desc"
     try:
         response = await http_client.get(url, timeout=15.0)
         response.raise_for_status()
         data = response.json()
         logger.info(f"Mediastack: Found {len(data.get('data', []))} articles for query '{query}'")
         # Adapt mapping if necessary (e.g., 'url', 'image', 'published_at')
         return data.get('data', [])
     except Exception as e:
         logger.error(f"Error fetching from Mediastack: {e}")
         return []

# --- Analysis Functions --- #

def parse_json_from_gemini_response(text: str) -> Optional[Dict[str, Any]]:
    """Tries to extract a JSON block from Gemini's response text."""
    try:
        # Search for the start and end of the JSON block, ignoring ```json``` if it exists
        text_cleaned = text.strip().removeprefix('```json').removesuffix('```').strip()
        json_start = text_cleaned.find('{')
        json_end = text_cleaned.rfind('}')
        if json_start != -1 and json_end != -1:
            json_str = text_cleaned[json_start:json_end+1]
            return json.loads(json_str)
        else:
            logger.warning(f"No JSON found in Gemini response: {text}")
            return None
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from Gemini: {e}. Response: {text}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error parsing JSON from Gemini: {e}")
        return None

async def analyze_with_gemini(title: Optional[str], description: Optional[str], published_at: Optional[datetime] = None) -> Dict[str, Any]:
    """Analyzes news title and description using Gemini API, including star rating and topicality check."""
    if not settings.GEMINI_API_KEY or not title:
        return {}

    content_to_analyze = f"Title: {title}"
    if description:
        content_to_analyze += f"\nSummary: {description[:1000]}"
    else:
        content_to_analyze += "\nSummary: (Not available)"
    
    if published_at:
        content_to_analyze += f"\nPublication Date: {published_at.strftime('%Y-%m-%d')}"

    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        # We get the current date in UTC to pass to the prompt
        current_date_utc = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
        prompt = f"""
Analyze the following news article based on its title, summary, and publication date.
The current date is {current_date_utc}.

Article content:
---
{content_to_analyze}
---

Your task is to return a JSON object with the following structure and logic:

1.  `is_current_week_news` (boolean): `true` if the article's publication date is within the last 7 days from the current date ({current_date_utc}). Otherwise, `false`.
2.  `star_rating` (float): A quality score from 3.0 to 5.0.
    -   Assign a rating ONLY IF `is_current_week_news` is `true`.
    -   The rating should reflect the quality, relevance, and depth of the content for a tech audience (developers, AI enthusiasts).
    -   3.0-3.5: Moderately interesting, generic news.
    -   3.6-4.5: Solid, well-explained article, a tutorial, or significant tech news.
    -   4.6-5.0: Exceptional, a must-read, deep analysis, or a major breakthrough.
    -   If `is_current_week_news` is `false`, this field MUST be `null`.
3.  `reasoning` (string): A brief, one-sentence explanation in English justifying your decisions for the two fields above. Example: "The article is recent and provides a deep dive into a new AI model." or "The article is over a week old, so it's not rated."
4.  `sectors` (array of strings): A list of 1 to 3 relevant tech sectors from the following list: ["AI & ML", "Software Development", "Cybersecurity", "Cloud & DevOps", "Hardware", "UI/UX & Design", "Fintech", "Healthtech", "Gaming", "General Tech"]. Select only the most relevant ones.
5.  `image_url_suggestion` (string or null): If you find a high-quality image URL in the text, suggest it. Otherwise, `null`.
6.  `relevance_score` (integer): An integer from 1 to 10 indicating the article's relevance to the "ivanintech" blog, which focuses on AI, automation, and web development. 10 is most relevant.

Return ONLY the JSON object.
"""
        response = await model.generate_content_async(prompt)
        text = response.text
        
        analysis = parse_json_from_gemini_response(text)

        if analysis:
            # Data validation and correction
            rating = analysis.get("star_rating")
            if rating is not None and not (3.0 <= rating <= 5.0):
                analysis["star_rating"] = None # Force to null if out of range
                logger.warning(f"Gemini returned star_rating out of range ({rating}) for: {title}. Adjusted to null.")

            return {
                "is_current_week_news": analysis.get("is_current_week_news", False),
                "star_rating": analysis.get("star_rating"),
                "reasoning": analysis.get("reasoning", ""),
                "sectors": analysis.get("sectors", []),
                "relevance_score": analysis.get("relevance_score")
            }
        else:
             logger.warning(f"Analysis with Gemini failed or returned unexpected format for: {title}")
             return {}

    except Exception as e:
        logger.error(f"Error calling Gemini API for '{title}': {e}", exc_info=True)
        return {}

async def delete_old_news():
    """Deletes old news items (older than 30 days) in a dedicated session."""
    async with AsyncSessionLocal() as db:
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

# --- Función Principal del Servicio --- #

async def fetch_and_store_news():
    """
    Main function to fetch news from all sources and store them individually.
    Each article is saved in its own transaction.
    """
    logger.info("Starting the news fetching and storing process...")
    
    # 1. Clean up old news first in its own transaction.
    await delete_old_news()

    # 2. Fetch all articles from all sources
    queries = ["artificial intelligence", "machine learning", "large language models", "python programming"]
    logger.info(f"Fetching news for queries: {queries}")
    tasks = [fetch_news_from_newsapi(http_client, q) for q in queries]
    tasks.extend([fetch_news_from_gnews(http_client, q) for q in queries])
    tasks.extend([fetch_news_from_mediastack(http_client, q) for q in queries])
    tasks.append(scrape_towards_data_science(http_client))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    all_articles = []
    for result in results:
        if isinstance(result, list): all_articles.extend(result)
        elif isinstance(result, Exception): logger.error(f"An API call failed during fetch: {result}", exc_info=True)
    
    logger.info(f"Total articles fetched: {len(all_articles)}. Now processing individually.")

    # 3. Process each article in its own transaction
    for article in all_articles:
        async with AsyncSessionLocal() as db:
            try:
                url = article.get('url')
                title = article.get('title')

                # Basic validation
                if not title or title == "[Removed]" or not is_valid_url(url):
                    continue

                # Check if URL already exists
                existing = await get_news_item_by_url(db, url=url)
                if existing:
                    continue

                # --- Enrichment and saving logic for ONE article ---
                # (The logic inside here is the same as before)
                published_at_str = article.get('publishedAt') or article.get('published_at')
                final_published_at = parse_datetime_flexible(published_at_str) or datetime.now(timezone.utc)
                image_url_api = article.get('image') or article.get('urlToImage')

                enriched_data = {}
                is_enriched = False
                if settings.GEMINI_API_KEY:
                    try:
                        logger.info(f"Enriching '{title[:50]}...'")
                        enriched_data = await analyze_with_gemini(title=title, description=article.get('description'), published_at=final_published_at)
                        is_enriched = bool(enriched_data)
                        await asyncio.sleep(2)
                    except Exception as e_gemini:
                        logger.error(f"Gemini enrichment failed for '{title[:50]}...': {e_gemini}")
                        is_enriched = False

                save_item = not is_enriched or (enriched_data.get("is_current_week_news") and enriched_data.get("star_rating") is not None)

                if save_item:
                    source_name = article.get('source', {}).get('name', 'Unknown Source')
                    source_id = article.get('source', {}).get('id')
                    
                    news_item_data = NewsItemCreate(
                        title=title, url=url, description=article.get('description'), author=article.get('author'),
                        content=article.get('content'), is_community=False, is_published=True, tags=[],
                        sectors=enriched_data.get("sectors", []), star_rating=enriched_data.get("star_rating"),
                        reasoning=enriched_data.get("reasoning"), imageUrl=image_url_api, publishedAt=final_published_at,
                        sourceName=f"{source_name} (Enriched)" if is_enriched else source_name, sourceId=source_id,
                        relevance_score=enriched_data.get("relevance_score"), is_current_week_news=enriched_data.get("is_current_week_news", False)
                    )
                    await create_news_item(db=db, news_item=news_item_data)
                    await db.commit()
                    logger.info(f"SUCCESSFULLY SAVED: {title[:60]}...")
            
            except Exception as e:
                logger.error(f"Failed to process and save article {article.get('url')}. Error: {e}", exc_info=True)
                await db.rollback()

            # --- RATE LIMITING ---
            # Wait for 5 seconds to not exceed the Gemini API's free tier limit (15 req/min)
            logger.info("Waiting for 5 seconds to respect API rate limit...")
            await asyncio.sleep(5)
            # --- END RATE LIMITING ---

    logger.info("News fetching and storing process completed.")

if __name__ == "__main__":
    # To run this service manually:
    # `python -m app.services.aggregated_news_service`
    # Make sure your environment (like a virtualenv) is activated
    # and the script is run as a module from the project's root directory.
    
    # Python's asyncio has different event loop policies depending on the OS.
    # On Windows, the default policy might not be compatible with certain
    # libraries. Setting the policy explicitly can prevent errors.
    if asyncio.get_event_loop().is_running():
         # If there's a running loop, just run the coroutine
         asyncio.run(fetch_and_store_news())
    else:
         # If no loop is running, create one
         asyncio.run(fetch_and_store_news())

# --- Fin del archivo ---