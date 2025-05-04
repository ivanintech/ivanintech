from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from typing import List, Optional
import logging

from app.db.models.blog_post import BlogPost
from app.schemas.blog import BlogPostCreate, BlogPostUpdate

logger = logging.getLogger(__name__)

async def get_blog_posts(db: AsyncSession, skip: int = 0, limit: int = 100, status: str = "published") -> List[BlogPost]:
    """Retrieve published blog posts, ordered by date descending."""
    logger.info(f"[CRUD] get_blog_posts llamado con skip={skip}, limit={limit}")
    # stmt = select(BlogPost).order_by(desc(BlogPost.published_date)).filter(BlogPost.status == status).offset(skip).limit(limit)
    # Consulta modificada para ignorar el status temporalmente
    stmt = select(BlogPost).order_by(desc(BlogPost.published_date)).offset(skip).limit(limit)
    logger.info(f"[CRUD] Ejecutando consulta: {stmt}")
    try:
        result = await db.execute(stmt)
        posts = result.scalars().all()
        logger.info(f"[CRUD] Consulta ejecutada. Posts encontrados: {len(posts)}")
        # Opcional: loguear los IDs si no son muchos
        if posts:
            logger.debug(f"[CRUD] IDs encontrados: {[p.id for p in posts]}")
        return posts
    except Exception as e:
        logger.error(f"[CRUD] Error al ejecutar consulta get_blog_posts: {e}", exc_info=True)
        raise

async def get_blog_post_by_slug(db: AsyncSession, slug: str) -> Optional[BlogPost]:
    """Retrieves a single blog post by its slug asynchronously."""
    stmt = select(BlogPost).filter(BlogPost.slug == slug)
    result = await db.execute(stmt)
    return result.scalars().first()

# Aquí podríamos añadir funciones CRUD adicionales en el futuro:
# async def create_blog_post(db: AsyncSession, *, post_data: schemas.BlogPostCreate) -> BlogPost:
#     db_post = BlogPost(**post_data.dict())
#     db.add(db_post)
#     await db.commit()
#     await db.refresh(db_post)
#     return db_post
# ... (update, delete async)

# --- Funciones Create, Update, Delete --- 

async def get_blog_post(db: AsyncSession, blog_post_id: int) -> Optional[BlogPost]:
    return await db.get(BlogPost, blog_post_id)

async def create_blog_post(db: AsyncSession, *, blog_post_in: BlogPostCreate, author_id: int) -> BlogPost:
    db_blog_post = BlogPost(
        **blog_post_in.dict(),
        author_id=author_id
    )
    if hasattr(blog_post_in, 'status') and blog_post_in.status:
        db_blog_post.status = blog_post_in.status
    if hasattr(blog_post_in, 'linkedin_post_url') and blog_post_in.linkedin_post_url:
        db_blog_post.linkedin_post_url = str(blog_post_in.linkedin_post_url)

    db.add(db_blog_post)
    await db.commit()
    await db.refresh(db_blog_post)
    return db_blog_post

async def update_blog_post(
    db: AsyncSession,
    *, 
    db_blog_post: BlogPost, 
    blog_post_in: BlogPostUpdate
) -> BlogPost:
    update_data = blog_post_in.dict(exclude_unset=True)

    if "linkedin_post_url" in update_data and update_data["linkedin_post_url"] is not None:
        update_data["linkedin_post_url"] = str(update_data["linkedin_post_url"])
    if "image_url" in update_data and update_data["image_url"] is not None:
        update_data["image_url"] = str(update_data["image_url"])

    for field, value in update_data.items():
        setattr(db_blog_post, field, value)

    db.add(db_blog_post)
    await db.commit()
    await db.refresh(db_blog_post)
    return db_blog_post

async def delete_blog_post(db: AsyncSession, *, db_blog_post: BlogPost):
    await db.delete(db_blog_post)
    await db.commit()

# ... 