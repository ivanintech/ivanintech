import sys
import os

# Añade la carpeta 'backend' (que contiene el paquete 'app') al sys.path
current_dir = os.path.dirname(__file__)
backend_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import asyncio
from app.db.session import async_session_maker
from app.db.models.news_item import NewsItem
from sqlalchemy import select
from datetime import datetime

async def main():
    async with async_session_maker() as session:
        # Buscar noticias sin fecha de publicación
        result = await session.execute(
            select(NewsItem).where((NewsItem.publishedAt == None) | (NewsItem.publishedAt == ""))
        )
        news_items = result.scalars().all()
        print(f"Found {len(news_items)} news items without publishedAt")

        for item in news_items:
            # Usa la fecha de creación como fallback, o la fecha actual si tampoco hay
            fallback_date = item.created_at or datetime.utcnow()
            item.publishedAt = fallback_date
            print(f"Updating news item {item.id} with publishedAt={item.publishedAt}")
        await session.commit()

if __name__ == "__main__":
    asyncio.run(main()) 