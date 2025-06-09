from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from app import crud
from app.db.session import get_db
from app.schemas.resource_link import ResourceLinkRead, ResourceLinkCreate, ResourceLinkUpdate
from app.db.models.user import User # Para el tipo de current_user
from app.api import deps # Para dependencias de autenticación
from app.services import gemini_service # <-- AÑADIDO

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=ResourceLinkRead, status_code=status.HTTP_201_CREATED)
async def create_resource_link_route(
    *, 
    db: AsyncSession = Depends(get_db),
    resource_link_in: ResourceLinkCreate,
    current_user: User = Depends(deps.get_current_user)
):
    """Create a new resource link. Requires superuser privileges."""
    logger.info(f"[API ResourceLink] User {current_user.email} creating resource link for URL: {resource_link_in.url}")

    # Generar detalles usando Gemini si no se proporcionaron todos
    generated_details = None
    try:
        logger.debug(f"Llamando a gemini_service para URL: {resource_link_in.url}")
        generated_details = await gemini_service.generate_resource_details(
            url=str(resource_link_in.url), # Asegurarse que es string
            user_title=resource_link_in.title,
            user_personal_note=resource_link_in.personal_note
        )
        logger.debug(f"Detalles de Gemini recibidos: {generated_details}")
    except Exception as e:
        logger.error(f"Error llamando a gemini_service.generate_resource_details para {resource_link_in.url}: {e}", exc_info=True)
        # No relanzar la excepción aquí, simplemente no tendremos los detalles generados por IA
        # o podríamos decidir lanzar un error 500 si la generación es crítica.
        # Por ahora, continuamos sin ellos.

    if generated_details:
        # Actualizar el objeto de entrada con los detalles generados por IA
        # si no fueron proporcionados explícitamente por el usuario o para mejorarlos.
        resource_link_in.title = generated_details.get("title") or resource_link_in.title
        resource_link_in.ai_generated_description = generated_details.get("ai_generated_description") or resource_link_in.ai_generated_description
        resource_link_in.personal_note = generated_details.get("personal_note") or resource_link_in.personal_note
        resource_link_in.resource_type = generated_details.get("resource_type") or resource_link_in.resource_type
        
        # Para los tags, podríamos querer combinarlos o dar preferencia a los de Gemini
        generated_tags = generated_details.get("tags")
        if isinstance(generated_tags, list):
            # Convertir lista de tags a string separado por comas si es necesario
            resource_link_in.tags = ", ".join(generated_tags) 
        elif isinstance(generated_tags, str):
            resource_link_in.tags = generated_tags
        # Si resource_link_in.tags ya tenía algo, decidir cómo combinar (aquí se sobrescribe si Gemini da algo)
        
        # Para thumbnail_url, solo lo usamos si no se proporcionó uno y Gemini lo sugiere
        if not resource_link_in.thumbnail_url and generated_details.get("thumbnail_url_suggestion"):
            # Aquí necesitaríamos validar si thumbnail_url_suggestion es un HttpUrl válido antes de asignarlo
            # Pydantic lo hará al crear el schema, pero es bueno tenerlo en cuenta.
            try:
                from pydantic import HttpUrl
                resource_link_in.thumbnail_url = HttpUrl(generated_details.get("thumbnail_url_suggestion"))
            except Exception as e:
                logger.warning(f"URL de thumbnail sugerida por IA no válida: {generated_details.get('thumbnail_url_suggestion')}. Error: {e}")

    logger.info(f"Datos finales para crear ResourceLink (después de Gemini): Título: '{resource_link_in.title}', Tipo: {resource_link_in.resource_type}")

    try:
        resource_link = await crud.resource_link.create_resource_link(
            db=db, 
            resource_link_in=resource_link_in, 
            author_id=current_user.id
        )
        # Preparar la respuesta con el nombre del autor
        author_name = current_user.full_name if current_user.full_name else current_user.email
        resource_link_data = resource_link.__dict__
        resource_link_data["author_name"] = author_name
        # is_pinned será False por defecto en el modelo y schema
        return ResourceLinkRead.model_validate(resource_link_data)
    except Exception as e:
        logger.error(f"[API ResourceLink] Error creating resource link '{resource_link_in.title}': {e}", exc_info=True)
        # Podríamos querer devolver un error más específico si la inserción falla debido a datos incorrectos de Gemini
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error creating resource link: {str(e)}")

@router.get("/", response_model=List[ResourceLinkRead])
async def read_resource_links_route(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    resource_type: Optional[str] = Query(None, description="Filter by resource type (e.g., Video, GitHub, Article)"),
    tags: Optional[str] = Query(None, description="Comma-separated tags to filter by (e.g., python,fastapi)")
):
    """Retrieve a list of resource links."""
    logger.info(f"[API ResourceLink] Reading resource links: skip={skip}, limit={limit}, type={resource_type}, tags={tags}")
    tags_list = tags.split(',') if tags else None
    db_resource_links = await crud.resource_link.get_resource_links(
        db=db, skip=skip, limit=limit, resource_type=resource_type, tags_contain=tags_list
    )
    # Mapear a ResourceLinkRead incluyendo author_name e is_pinned
    response_links = []
    for link in db_resource_links:
        author_name = link.author.full_name if link.author and link.author.full_name else (link.author.email if link.author else "Unknown User")
        response_links.append(
            ResourceLinkRead(
                id=link.id,
                title=link.title,
                url=str(link.url), # Asegurar que es string
                ai_generated_description=link.ai_generated_description,
                personal_note=link.personal_note,
                resource_type=link.resource_type,
                tags=link.tags,
                thumbnail_url=str(link.thumbnail_url) if link.thumbnail_url else None,
                created_at=link.created_at,
                author_id=link.author_id,
                author_name=author_name,
                is_pinned=link.is_pinned
            )
        )
    return response_links

@router.get("/{resource_id}", response_model=ResourceLinkRead)
async def read_resource_link_route(resource_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve a specific resource link by ID."""
    logger.info(f"[API ResourceLink] Reading resource link by ID: {resource_id}")
    db_resource_link = await crud.resource_link.get_resource_link(db=db, resource_link_id=resource_id)
    if db_resource_link is None:
        logger.warning(f"[API ResourceLink] Resource link with ID '{resource_id}' not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource link not found")
    
    author_name = db_resource_link.author.full_name if db_resource_link.author and db_resource_link.author.full_name else (db_resource_link.author.email if db_resource_link.author else "Unknown User")
    return ResourceLinkRead(
        id=db_resource_link.id,
        title=db_resource_link.title,
        url=str(db_resource_link.url),
        ai_generated_description=db_resource_link.ai_generated_description,
        personal_note=db_resource_link.personal_note,
        resource_type=db_resource_link.resource_type,
        tags=db_resource_link.tags,
        thumbnail_url=str(db_resource_link.thumbnail_url) if db_resource_link.thumbnail_url else None,
        created_at=db_resource_link.created_at,
        author_id=db_resource_link.author_id,
        author_name=author_name,
        is_pinned=db_resource_link.is_pinned
    )

@router.put("/{resource_id}", response_model=ResourceLinkRead)
async def update_resource_link_route(
    *, 
    db: AsyncSession = Depends(get_db),
    resource_id: str,
    resource_link_in: ResourceLinkUpdate,
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """Update an existing resource link. Requires superuser privileges."""
    logger.info(f"[API ResourceLink] User {current_user.email} updating resource link ID: {resource_id}")
    db_resource_link = await crud.resource_link.get_resource_link(db=db, resource_link_id=resource_id)
    if not db_resource_link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource link not found")
    
    # Aquí también se podría integrar la lógica de IA si la actualización de la URL debe regenerar descripciones
    
    updated_resource_link = await crud.resource_link.update_resource_link(
        db=db, db_obj=db_resource_link, obj_in=resource_link_in
    )
    return updated_resource_link

@router.delete("/{resource_id}", response_model=ResourceLinkRead) # O devuelve un Message schema o status 204
async def delete_resource_link_route(
    *, 
    db: AsyncSession = Depends(get_db),
    resource_id: str,
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """Delete a resource link. Requires superuser privileges."""
    logger.info(f"[API ResourceLink] User {current_user.email} deleting resource link ID: {resource_id}")
    db_resource_link = await crud.resource_link.get_resource_link(db=db, resource_link_id=resource_id)
    if not db_resource_link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource link not found")
    
    deleted_resource_link = await crud.resource_link.delete_resource_link(db=db, db_obj=db_resource_link)
    # Si delete_resource_link devolviera None o un booleano, ajustar el response_model a Message o status_code=204
    return deleted_resource_link

# --- Nuevas rutas para Pinning ---
@router.post("/{resource_id}/pin", response_model=ResourceLinkRead)
async def pin_resource_link_route(
    resource_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser) # Solo superusuarios pueden fijar
):
    """Pin a resource link. Requires superuser privileges."""
    logger.info(f"[API ResourceLink] User {current_user.email} pinning resource link ID: {resource_id}")
    db_resource_link = await crud.resource_link.get_resource_link(db=db, resource_link_id=resource_id)
    if not db_resource_link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource link not found")
    
    if db_resource_link.is_pinned:
        # Podríamos devolver un 304 Not Modified o simplemente el objeto actual
        logger.info(f"[API ResourceLink] Resource link {resource_id} is already pinned.")
    else:
        db_resource_link.is_pinned = True
        db.add(db_resource_link)
        await db.commit()
        await db.refresh(db_resource_link)
        logger.info(f"[API ResourceLink] Resource link {resource_id} has been pinned.")

    author_name = db_resource_link.author.full_name if db_resource_link.author and db_resource_link.author.full_name else (db_resource_link.author.email if db_resource_link.author else "Unknown User")
    return ResourceLinkRead.model_validate(db_resource_link) # Usar model_validate

@router.post("/{resource_id}/unpin", response_model=ResourceLinkRead)
async def unpin_resource_link_route(
    resource_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser) # Solo superusuarios pueden desfijar
):
    """Unpin a resource link. Requires superuser privileges."""
    logger.info(f"[API ResourceLink] User {current_user.email} unpinning resource link ID: {resource_id}")
    db_resource_link = await crud.resource_link.get_resource_link(db=db, resource_link_id=resource_id)
    if not db_resource_link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource link not found")

    if not db_resource_link.is_pinned:
        logger.info(f"[API ResourceLink] Resource link {resource_id} is already unpinned.")
    else:
        db_resource_link.is_pinned = False
        db.add(db_resource_link)
        await db.commit()
        await db.refresh(db_resource_link)
        logger.info(f"[API ResourceLink] Resource link {resource_id} has been unpinned.")
    
    author_name = db_resource_link.author.full_name if db_resource_link.author and db_resource_link.author.full_name else (db_resource_link.author.email if db_resource_link.author else "Unknown User")
    return ResourceLinkRead.model_validate(db_resource_link) # Usar model_validate 