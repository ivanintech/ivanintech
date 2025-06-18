# app/api/routes/blog.py
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession # Switch to AsyncSession
# from sqlalchemy.orm import Session # No longer used
import logging

# Import necessary schemas
from app.schemas.blog import BlogPostRead, BlogPostCreate, BlogPostUpdate # Add BlogPostCreate and Update
# from app.db_mock import blog_posts_db # No longer used
from app import crud, schemas
from app.db import models
from app.api import deps # For authentication dependencies
from app.schemas.msg import Message # If used for responses
from app.db.models.user import User # For the current_user type
from app.core.config import settings

router = APIRouter()

logger = logging.getLogger(__name__) # Make sure the logger is here too

# Route to create a new blog post
@router.post("/", response_model=BlogPostRead, status_code=status.HTTP_201_CREATED)
async def create_blog_post_route(
    *,
    db: AsyncSession = Depends(deps.get_db),
    blog_post_in: BlogPostCreate,
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """Create new blog post. Requires superuser privileges."""
    logger.info(f"[API Blog] User {current_user.email} attempting to create blog post: {blog_post_in.title}")
    try:
        blog_post = await crud.blog_post.create_with_author(db=db, obj_in=blog_post_in, author_id=current_user.id)
        logger.info(f"[API Blog] Blog post '{blog_post.title}' (ID: {blog_post.id}) created successfully.")
        return blog_post
    except Exception as e:
        # The CRUD might have thrown an error (e.g., for a duplicate slug if regeneration is not handled there)
        logger.error(f"[API Blog] Error creating blog post '{blog_post_in.title}': {e}", exc_info=True)
        # Here you might want to map specific DB/CRUD errors to more specific HTTP errors
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error creating blog post")

# Route to read multiple blog posts (base route of the blog router)
@router.get("/", response_model=schemas.blog.BlogPostList)
async def read_blog_posts(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    status_filter: schemas.blog.BlogPostStatus = None,
    current_user: models.User = Depends(deps.get_current_user_or_none),
):
    """Retrieve blog posts. Optionally filter by status."""
    logger.info(f"[API Blog] Reading blog posts with skip={skip}, limit={limit}, status_filter={status_filter}")
    try:
        posts = await crud.blog_post.get_multi(db=db, skip=skip, limit=limit, status=status_filter)
        logger.info(f"[API Blog] Found {len(posts)} blog posts.")
        if posts is None:
            posts = []
        return {"items": posts}
    except Exception as e:
        logger.error(f"[API Blog] Error reading blog posts: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error retrieving blog posts")

# Route to read a specific blog post by SLUG
@router.get("/{slug}", response_model=BlogPostRead)
async def read_blog_post_by_slug_route(slug: str, db: AsyncSession = Depends(deps.get_db)):
    """Retrieve a specific blog post by slug."""
    logger.info(f"[API Blog] Reading blog post by slug: {slug}")
    db_post = await crud.blog_post.get_by_slug(db=db, slug=slug)
    if db_post is None:
        logger.warning(f"[API Blog] Blog post with slug '{slug}' not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog post not found")
    return db_post

# Route to read a specific blog post by ID (optional, but good to have)
@router.get("/id/{post_id}", response_model=BlogPostRead, name="read_blog_post_by_id")
async def read_blog_post_by_id_route(post_id: str, db: AsyncSession = Depends(deps.get_db)):
    """Retrieve a specific blog post by its ID."""
    logger.info(f"[API Blog] Reading blog post by ID: {post_id}")
    db_post = await crud.blog_post.get(db=db, id=post_id)
    if db_post is None:
        logger.warning(f"[API Blog] Blog post with ID '{post_id}' not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog post not found")
    return db_post

# PUT and DELETE could be added here in the future
# @router.put("/{post_id}", response_model=BlogPostRead)
# async def update_blog_post_route(...)

# @router.delete("/{post_id}", response_model=Message)
# async def delete_blog_post_route(...) 