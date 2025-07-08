# app/api/routes/blog.py
from fastapi import APIRouter, HTTPException, Depends, status, Query
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
from app.services.supabase_service import supabase_service

router = APIRouter()

logger = logging.getLogger(__name__) # Make sure the logger is here too

# === FALLBACK ROUTES USING SUPABASE REST API ===

@router.get("/supabase", response_model=dict)
async def read_blog_posts_supabase(
    skip: int = 0,
    limit: int = 100,
    show_automated: bool = False,
):
    """
    Retrieve blog posts using Supabase REST API (fallback when PostgreSQL is unavailable).
    """
    logger.info(f"[API Blog Supabase] Reading blog posts with skip={skip}, limit={limit}, show_automated={show_automated}")
    try:
        posts = await supabase_service.get_blog_posts(
            skip=skip, limit=limit, show_automated=show_automated
        )
        logger.info(f"[API Blog Supabase] Found {len(posts)} blog posts.")
        return {"items": posts}
    except Exception as e:
        logger.error(f"[API Blog Supabase] Error reading blog posts: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error retrieving blog posts")

@router.get("/supabase/{slug}", response_model=dict)
async def read_blog_post_by_slug_supabase(slug: str):
    """Retrieve a specific blog post by slug using Supabase REST API."""
    logger.info(f"[API Blog Supabase] Reading blog post by slug: {slug}")
    try:
        post = await supabase_service.get_blog_post_by_slug(slug)
        if post is None:
            logger.warning(f"[API Blog Supabase] Blog post with slug '{slug}' not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog post not found")
        return post
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[API Blog Supabase] Error reading blog post by slug: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error retrieving blog post")

# === ORIGINAL ROUTES WITH POSTGRESQL ===

# Route to create a new blog post
@router.post("/", response_model=BlogPostRead, status_code=status.HTTP_201_CREATED)
async def create_blog_post_route(
    *,
    db: deps.SessionDep,
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

# Route to read multiple blog posts (base route of the blog router) - DIRECT SUPABASE
@router.get(
    "/",
    response_model=schemas.blog.BlogPostList,
    summary="Get a paginated list of blog posts",
)
async def read_blog_posts(
    db: deps.SessionDep,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Posts per page"),
    show_automated: bool = False, # New parameter to control visibility
    current_user: models.User = Depends(deps.get_current_user_or_none),
):
    """
    Retrieve blog posts.
    - By default, only returns posts with a LinkedIn URL (human-created).
    - Set show_automated=true to include all posts.
    - Uses Supabase REST API directly for faster response.
    """
    logger.info(f"[API Blog] Reading blog posts with page={page}, per_page={per_page}, show_automated={show_automated}")
    
    # GO DIRECTLY TO SUPABASE FOR FASTER RESPONSE
    try:
        posts = await supabase_service.get_blog_posts(
            skip=(page - 1) * per_page, limit=per_page, show_automated=show_automated
        )
        logger.info(f"[API Blog Direct] Found {len(posts)} blog posts via Supabase API.")
        return {"items": posts}
    except Exception as e:
        logger.error(f"[API Blog Direct] Error with Supabase API: {e}", exc_info=True)
        # Return empty list as fallback
        return {"items": []}

# Route to read a specific blog post by SLUG - WITH FALLBACK
@router.get(
    "/{slug}",
    response_model=BlogPostRead,
    summary="Get a specific blog post by its slug",
)
async def read_blog_post_by_slug_route(slug: str, db: deps.SessionDep):
    """Retrieve a specific blog post by slug with fallback to Supabase REST API."""
    logger.info(f"[API Blog] Reading blog post by slug: {slug}")
    try:
        db_post = await crud.blog_post.get_by_slug(db=db, slug=slug)
        if db_post is None:
            logger.warning(f"[API Blog] Blog post with slug '{slug}' not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog post not found")
        return db_post
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[API Blog] PostgreSQL error, falling back to Supabase REST API: {e}")
        try:
            post = await supabase_service.get_blog_post_by_slug(slug)
            if post is None:
                logger.warning(f"[API Blog Fallback] Blog post with slug '{slug}' not found.")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog post not found")
            return post
        except HTTPException:
            raise
        except Exception as fallback_e:
            logger.error(f"[API Blog Fallback] Error with Supabase API: {fallback_e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error retrieving blog post")

# Route to read a specific blog post by ID (optional, but good to have)
@router.get(
    "/{post_id}",
    response_model=BlogPostRead,
    summary="Get a specific blog post by its ID",
)
async def read_blog_post_by_id_route(post_id: str, db: deps.SessionDep):
    """Retrieve a specific blog post by its ID."""
    logger.info(f"[API Blog] Reading blog post by ID: {post_id}")
    db_post = await crud.blog_post.get(db=db, id=post_id)
    if db_post is None:
        logger.warning(f"[API Blog] Blog post with ID '{post_id}' not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog post not found")
    return db_post

@router.put(
    "/{post_id}",
    response_model=BlogPostRead,
    dependencies=[Depends(deps.get_current_active_superuser)],
)
async def update_blog_post(
    post_id: str,
    blog_post_in: BlogPostUpdate,
    db: deps.SessionDep,
):
    """
    Update a blog post. Superuser only.
    """
    blog_post = await crud.blog_post.get(db=db, id=post_id)
    if not blog_post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    updated_post = await crud.blog_post.update(db=db, db_obj=blog_post, obj_in=blog_post_in)
    return updated_post

@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(deps.get_current_active_superuser)],
)
async def delete_blog_post(
    post_id: str,
    db: deps.SessionDep,
):
    """
    Delete a blog post. Superuser only.
    """
    blog_post = await crud.blog_post.get(db=db, id=post_id)
    if not blog_post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    await crud.blog_post.remove(db=db, id=post_id)
    return None 