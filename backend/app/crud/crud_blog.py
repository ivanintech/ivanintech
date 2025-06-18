import re
import uuid
from datetime import date # Asegúrate que date esté importado de datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc # Asegúrate que desc esté importado
from typing import List, Optional
import logging
from sqlalchemy.orm import selectinload

from app.db.models.blog_post import BlogPost
from app.schemas.blog import BlogPostCreate, BlogPostUpdate
from app.crud.base import CRUDBase

logger = logging.getLogger(__name__)

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[\s\W-]+', '-', text)  # Reemplaza espacios y no alfanuméricos (excepto -) con -
    text = text.strip('-')
    # Considerar truncar el slug a una longitud máxima si es necesario
    return text

def generate_slug(title: str) -> str:
    s = title.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_-]+', '-', s)
    s = re.sub(r'^-+|-+$', '', s)
    return s

async def get_blog_posts(db: AsyncSession, skip: int = 0, limit: int = 100, status: str = "published") -> List[BlogPost]:
    """Retrieve published blog posts, ordered by date descending."""
    logger.info(f"[CRUD] get_blog_posts llamado con skip={skip}, limit={limit}, status={status}")
    # stmt = select(BlogPost).order_by(desc(BlogPost.published_date)).filter(BlogPost.status == status).offset(skip).limit(limit)
    # Consulta modificada para ignorar el status temporalmente si se quitó del modelo o para pruebas
    stmt = select(BlogPost).order_by(desc(BlogPost.published_date)).offset(skip).limit(limit)
    if status: # Si se provee un status, filtrar por él.
        stmt = stmt.filter(BlogPost.status == status)
        
    logger.info(f"[CRUD] Ejecutando consulta: {stmt}")
    try:
        result = await db.execute(stmt)
        posts = result.scalars().all()
        logger.info(f"[CRUD] Consulta ejecutada. Posts encontrados: {len(posts)}")
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

async def get_blog_post(db: AsyncSession, blog_post_id: str) -> Optional[BlogPost]: # Cambiado blog_post_id a str
    # .get() funciona con la clave primaria, que es str para BlogPost
    return await db.get(BlogPost, blog_post_id)

async def create_blog_post(db: AsyncSession, *, blog_post_in: BlogPostCreate, author_id: int) -> BlogPost:
    generated_slug = slugify(blog_post_in.title)
    # Aquí se debería añadir una lógica para asegurar la unicidad del slug si es necesario.
    # Por ejemplo, consultando la base de datos y añadiendo un sufijo si ya existe.
    # Simplificación: Se asume que el título generará un slug suficientemente único o se manejará error de BD.

    db_obj_data = blog_post_in.dict(exclude_unset=True)
    
    new_id = uuid.uuid4().hex

    db_blog_post = BlogPost(
        **db_obj_data,
        id=new_id,
        slug=generated_slug,
        author_id=author_id,
        published_date=date.today() # Establecer fecha de publicación actual
    )
    
    # Asegurar que los campos opcionales que son URLs se manejen como strings si es necesario
    # Pydantic v2 debería manejar la conversión de HttpUrl a str en .dict() si el tipo es HttpUrl | str
    # Si image_url o linkedin_post_url están en db_obj_data y son HttpUrl, se convertirán.
    # No es necesario hacer str() explícito aquí si los schemas están bien definidos.

    db.add(db_blog_post)
    try:
        await db.commit()
    except Exception as e: # Capturar error de commit (ej. violación de unicidad de slug)
        await db.rollback()
        logger.error(f"[CRUD] Error al hacer commit para nuevo blog post (slug: {generated_slug}): {e}", exc_info=True)
        # Podrías querer lanzar una excepción HTTP específica aquí si esto se llama desde una API
        raise 
    await db.refresh(db_blog_post)
    return db_blog_post

async def update_blog_post(
    db: AsyncSession,
    *, 
    db_blog_post: BlogPost, 
    blog_post_in: BlogPostUpdate
) -> BlogPost:
    update_data = blog_post_in.dict(exclude_unset=True)

    # Si se actualiza el título, opcionalmente se podría regenerar y actualizar el slug
    # Esto requiere cuidado por el impacto en SEO y enlaces existentes.
    if "title" in update_data and db_blog_post.title != update_data["title"]:
        new_slug = slugify(update_data["title"])
        # Aquí también se necesitaría lógica de unicidad para el nuevo slug
        setattr(db_blog_post, 'slug', new_slug)


    # Pydantic v2 debería manejar la conversión de HttpUrl a str en .dict()
    # No se necesitan conversiones explícitas a str para image_url y linkedin_post_url aquí.

    for field, value in update_data.items():
        setattr(db_blog_post, field, value)
    
    # Actualizar last_modified_date si el modelo no lo hace automáticamente con onupdate
    # El modelo tiene onupdate=date.today para last_modified_date, pero es para tipo Date.
    # Si es un campo DateTime, func.now() es mejor. SQLAlchemy podría manejarlo.
    # Si no, podemos setearlo explícitamente:
    # db_blog_post.last_modified_date = date.today()


    db.add(db_blog_post)
    await db.commit()
    await db.refresh(db_blog_post)
    return db_blog_post

async def delete_blog_post(db: AsyncSession, *, db_blog_post: BlogPost):
    await db.delete(db_blog_post)
    await db.commit()

# ... 

class CRUDBlogPost(CRUDBase[BlogPost, BlogPostCreate, BlogPostUpdate]):
    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100, status: Optional[str] = None
    ) -> list[BlogPost]:
        statement = (
            select(self.model)
            .offset(skip)
            .limit(limit)
            .options(selectinload(self.model.author))
            .order_by(self.model.published_date.desc())
        )
        if status:
            statement = statement.where(self.model.status == status)
            
        result = await db.execute(statement)
        return result.scalars().all()

    async def get_by_slug(self, db: AsyncSession, *, slug: str) -> Optional[BlogPost]:
        statement = (
            select(self.model)
            .where(self.model.slug == slug)
            .options(selectinload(self.model.author))
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def create_with_author(
        self, db: AsyncSession, *, obj_in: BlogPostCreate, author_id: int
    ) -> BlogPost:
        slug = generate_slug(obj_in.title)
        db_obj = self.model(**obj_in.model_dump(), author_id=author_id, slug=slug)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

blog_post = CRUDBlogPost(BlogPost) 