import asyncio
import httpx
import logging
import feedparser

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("news_verify_standalone")

async def minimal_rss_fetch(client: httpx.AsyncClient, feed_url: str):
    """Minimal standalone implementation of _fetch_from_rss_feed logic."""
    logger.info(f"Fetching from RSS feed: {feed_url}")
    try:
        response = await client.get(feed_url, timeout=30.0, follow_redirects=True)
        response.raise_for_status()
        
        parsed_feed = feedparser.parse(response.text)
        if not parsed_feed.entries:
            logger.warning(f"RSS feed {feed_url} has no entries")
            return []

        articles = []
        for entry in parsed_feed.entries:
            if not entry.get("title") or not entry.get("link"):
                continue
            
            # Simple mapping to our expected format
            articles.append({
                "title": entry.get("title").strip(),
                "url": entry.get("link"),
                "source": {"name": parsed_feed.feed.get("title", feed_url)},
                "publishedAt": entry.get("published") or entry.get("updated")
            })
        return articles
    except Exception as e:
        logger.error(f"Error in minimal fetch: {e}")
        return []

async def verify_pipeline():
    test_feed = "https://feeds.feedburner.com/TechCrunch/"
    logger.info(f"Step 1: Fetching from RSS: {test_feed}")
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        articles = await minimal_rss_fetch(client, test_feed)
        
        if not articles:
            logger.error("Failed to fetch articles.")
            return

        logger.info(f"Successfully fetched {len(articles)} articles.")
        for idx, article in enumerate(articles[:3]):
            logger.info(f"Article {idx+1}: {article.get('title')} - {article.get('url')}")

    logger.info("✅ Extraction logic successfully verified (Standalone mode).")

if __name__ == "__main__":
    asyncio.run(verify_pipeline())
