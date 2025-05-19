# app/api/routes/blog.py
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession # Cambiar a AsyncSession
# from sqlalchemy.orm import Session # Ya no se usa
import logging

# Importar schemas necesarios
from app.schemas.blog import BlogPostRead, BlogPostCreate, BlogPostUpdate # Añadir BlogPostCreate y Update
# from app.db_mock import blog_posts_db # Ya no se usa
from app import crud
from app.db.session import get_db
from app.api import deps # Para las dependencias de autenticación
from app.schemas.msg import Message # Si se usa para respuestas
from app.db.models.user import User # Para el tipo de current_user

router = APIRouter()

logger = logging.getLogger(__name__) # Asegurarse que el logger está aquí también

# Ruta para crear un nuevo blog post
@router.post("/", response_model=BlogPostRead, status_code=status.HTTP_201_CREATED)
async def create_blog_post_route(
    *,
    db: AsyncSession = Depends(get_db),
    blog_post_in: BlogPostCreate,
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """Create new blog post. Requires superuser privileges."""
    logger.info(f"[API Blog] User {current_user.email} attempting to create blog post: {blog_post_in.title}")
    try:
        # La función CRUD create_blog_post ya maneja la generación de slug, id, published_date
        blog_post = await crud.blog.create_blog_post(db=db, blog_post_in=blog_post_in, author_id=current_user.id)
        logger.info(f"[API Blog] Blog post '{blog_post.title}' (ID: {blog_post.id}) created successfully.")
        return blog_post
    except Exception as e:
        # El CRUD podría haber lanzado un error (ej. por slug duplicado si no se maneja la regeneración allí)
        logger.error(f"[API Blog] Error creating blog post '{blog_post_in.title}': {e}", exc_info=True)
        # Aquí podrías querer mapear errores específicos de la BD/CRUD a errores HTTP más específicos
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error creating blog post")

# Ruta para leer múltiples blog posts (ruta base del router de blog)
@router.get("/", response_model=List[BlogPostRead]) # Cambiado de "/blog" a "/"
async def read_blog_posts(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    status_filter: Optional[str] = None # Renombrado para claridad, era 'status' en CRUD
):
    """Retrieve blog posts. Optionally filter by status."""
    logger.info(f"[API Blog] Reading blog posts with skip={skip}, limit={limit}, status_filter={status_filter}")
    try:
        posts = await crud.blog.get_blog_posts(db=db, skip=skip, limit=limit, status=status_filter if status_filter else "published")
        logger.info(f"[API Blog] Found {len(posts)} blog posts.")
        return posts
    except Exception as e:
        logger.error(f"[API Blog] Error reading blog posts: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error retrieving blog posts")

# Ruta para leer un blog post específico por SLUG
@router.get("/{slug}", response_model=BlogPostRead) # Cambiado de "/blog/{slug}" a "/{slug}"
async def read_blog_post_by_slug_route(slug: str, db: AsyncSession = Depends(get_db)):
    """Retrieve a specific blog post by slug."""
    logger.info(f"[API Blog] Reading blog post by slug: {slug}")
    db_post = await crud.blog.get_blog_post_by_slug(db=db, slug=slug)
    if db_post is None:
        logger.warning(f"[API Blog] Blog post with slug '{slug}' not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog post not found")
    return db_post

# Ruta para leer un blog post específico por ID (opcional, pero bueno tenerla)
@router.get("/id/{post_id}", response_model=BlogPostRead, name="read_blog_post_by_id")
async def read_blog_post_by_id_route(post_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve a specific blog post by its ID."""
    logger.info(f"[API Blog] Reading blog post by ID: {post_id}")
    db_post = await crud.blog.get_blog_post(db=db, blog_post_id=post_id) # crud.blog.get_blog_post espera str
    if db_post is None:
        logger.warning(f"[API Blog] Blog post with ID '{post_id}' not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog post not found")
    return db_post

# Aquí se podrían añadir PUT y DELETE en el futuro
# @router.put("/{post_id}", response_model=BlogPostRead)
# async def update_blog_post_route(...)

# @router.delete("/{post_id}", response_model=Message)
# async def delete_blog_post_route(...) 