import feedparser
import httpx
import asyncio
import json

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

FEEDS = {
    "AlphaSignal": "https://alphasignalai.substack.com/feed",
    "TLDR_AI": "https://tldr.tech/ai/rss",
    "TLDR_Tech": "https://tldr.tech/rss",
    "TheRundown": "https://www.therundown.ai/feed",
    "DeepMind": "https://deepmind.google/blog/rss.xml",
    "OpenAI": "https://openai.com/news/rss",
    "MIT_Tech_Review_AI": "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
}

async def test_feeds():
    results = {}
    async with httpx.AsyncClient(follow_redirects=True, headers=BROWSER_HEADERS) as client:
        for name, url in FEEDS.items():
            res = {"url": url, "status": "failed"}
            try:
                resp = await client.get(url, timeout=15)
                res["http_status"] = resp.status_code
                if resp.status_code == 200:
                    d = feedparser.parse(resp.text)
                    res["title"] = d.feed.get('title', 'No Title')
                    res["entries_count"] = len(d.entries)
                    if d.entries:
                        res["sample_entry"] = d.entries[0].title
                    res["status"] = "success"
                else:
                    res["content_preview"] = resp.text[:200]
            except Exception as e:
                res["error"] = str(e)
            results[name] = res
    
    with open("feed_test_results_v4.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    asyncio.run(test_feeds())
