# app/api/routes/blog.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession # Cambiar a AsyncSession
from sqlalchemy.orm import Session
# from sqlalchemy.orm import Session # Ya no se usa
import logging

# Importar ambos schemas
from app.schemas.blog import BlogPostRead
# from app.db_mock import blog_posts_db # Ya no se usa
from app import crud
from app.db.session import get_db
from app.api import deps
from app.schemas.msg import Message
from app.db.models.user import User

router = APIRouter()

logger = logging.getLogger(__name__) # Asegurarse que el logger está aquí también

# Convertir a async
@router.get("/blog", response_model=List[BlogPostRead])
async def read_blog_posts(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Retrieve blog post previews asynchronously from the database via CRUD layer."""
    logger.info("****** [API Route] Entrando en read_blog_posts ******") # LOG AÑADIDO AL INICIO
    # Llamar con await
    try:
        logger.info("[API Route] Intentando llamar a crud.blog.get_blog_posts...") # Log antes de CRUD
        posts = await crud.blog.get_blog_posts(db=db, skip=skip, limit=limit)
        logger.info(f"[API Route] crud.blog.get_blog_posts devolvió {len(posts)} posts.") # Log después de CRUD
        return posts
    except Exception as e:
        logger.error(f"[API Route] Error en read_blog_posts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error retrieving blog posts")

# Convertir a async
@router.get("/blog/{slug}", response_model=BlogPostRead)
async def read_blog_post(slug: str, db: AsyncSession = Depends(get_db)):
    """Retrieve a specific blog post by slug asynchronously from the database via CRUD layer."""
    # Llamar con await
    db_post = await crud.blog.get_blog_post_by_slug(db=db, slug=slug)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post

# Podríamos añadir endpoints para crear posts, etc. 