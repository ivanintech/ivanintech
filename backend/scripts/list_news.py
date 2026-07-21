
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session_maker
from app.db.models.news_item import NewsItem
from sqlalchemy import select

async def list_news():
    print("Listing news items from SQLite...")
    async with async_session_maker() as db:
        result = await db.execute(select(NewsItem).order_by(NewsItem.publishedAt.desc()))
        items = result.scalars().all()
        
        print(f"Total News Items: {len(items)}")
        print("-" * 50)
        for item in items:
            print(f"Title: {item.title}")
            print(f"Source: {item.sourceName}")
            print(f"Published: {item.publishedAt}")
            print(f"URL: {item.url}")
            print("-" * 30)

if __name__ == "__main__":
    asyncio.run(list_news())
