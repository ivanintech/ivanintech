import csv
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import asyncio
import os

from app.db.session import AsyncSessionLocal
from app.db.models.blog_post import BlogPost
from app.db.models.user import User

CSV_PATH = os.path.join(os.path.dirname(__file__), "blog_posts.csv")
AUTHOR_ID = 1  # Cambia esto si quieres otro autor

async def import_posts():
    async with AsyncSessionLocal() as session:
        with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)  # Saltar la cabecera
            for row in reader:
                # Ajusta los índices según tu CSV
                # Ejemplo: [id, author_id, published_date, ..., category, ..., embed, status, title, slug, content, excerpt]
                post_id = row[0]
                published_date = row[2]
                category = row[4]
                embed = row[6]
                status = row[7]
                title = row[8]
                slug = row[9]
                content = row[10]
                excerpt = row[11] if len(row) > 11 else None

                # Verifica si ya existe el post (por slug o id)
                exists = await session.execute(select(BlogPost).where(BlogPost.slug == slug))
                if exists.scalars().first():
                    print(f"Post '{slug}' ya existe, saltando.")
                    continue

                post = BlogPost(
                    id=post_id,
                    title=title,
                    content=content if content else embed,
                    excerpt=excerpt,
                    tags=category,
                    image_url=None,
                    linkedin_post_url=None,
                    status=status,
                    slug=slug,
                    author_id=AUTHOR_ID,
                    published_date=datetime.strptime(published_date, "%Y-%m-%d").date() if published_date else None
                )
                session.add(post)
            await session.commit()
            print("Importación completada.")

if __name__ == "__main__":
    asyncio.run(import_posts())