import logging
from datetime import date # Importar date

from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.schemas.user import UserCreate # Import UserCreate
from app.core.config import settings # Import settings
# from app.schemas.project import ProjectCreate # Ya no la usamos aquí
from app.db import initial_data
from app.db.models.project import Project # Importar el modelo
from app.db.models.blog_post import BlogPost # Importar modelo BlogPost

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db(db: AsyncSession) -> None:
    """
    Inicializa la base de datos con datos iniciales si es necesario.
    Verifica si los proyectos y posts ya existen antes de insertarlos.
    """
    logger.info("Iniciando inicialización de la base de datos...")
    
    # --- Crear Superusuario si no existe ---
    logger.info("Verificando/creando superusuario inicial...")
    if not settings.FIRST_SUPERUSER:
        logger.warning(
            "FIRST_SUPERUSER no está configurado en las variables de entorno. "
            "Omitiendo creación de superusuario."
        )
    else:
        user = await crud.user.get_user_by_email(db, email=settings.FIRST_SUPERUSER)
        if not user:
            logger.info(f"Creando superusuario: {settings.FIRST_SUPERUSER}")
            user_in = UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                full_name="Admin", # Puedes cambiar esto o hacerlo configurable
                is_superuser=True,
                is_active=True, # Superuser debe estar activo por defecto
            )
            try:
                await crud.user.create_user(db=db, user_in=user_in)
                logger.info("Superusuario creado exitosamente.")
            except Exception as e:
                logger.error(f"Error al crear superusuario: {e}", exc_info=True)
                # Considerar si se debe hacer rollback o relanzar la excepción aquí
                # dependiendo de si la creación del superusuario es crítica para el inicio
                await db.rollback() # Rollback para este intento de creación
                # raise # Podrías relanzar si es crítico que el superusuario exista
        else:
            logger.info(f"Superusuario {settings.FIRST_SUPERUSER} ya existe.")
    
    # --- Poblar Proyectos ---
    logger.info("Verificando/poblando proyectos iniciales...")
    projects_created_count = 0
    projects_to_add = [] # Lista para añadir en batch
    
    for project_data in initial_data.initial_projects:
        project_id = project_data.get("id")
        if not project_id:
            logger.warning(f"Proyecto en initial_data sin ID, omitiendo: {project_data.get('title')}")
            continue
            
        existing_project = await crud.portfolio.get_project(db, project_id=project_id)
        
        if not existing_project:
            logger.info(f"Preparando creación de proyecto con ID: {project_id}")
            
            # --- Crear instancia del MODELO directamente --- #
            # Copiar el diccionario para no modificar el original
            model_data = project_data.copy()
            
            # Convertir HttpUrl a string si existen
            if model_data.get("githubUrl") is not None:
                model_data["githubUrl"] = str(model_data["githubUrl"])
            if model_data.get("liveUrl") is not None:
                model_data["liveUrl"] = str(model_data["liveUrl"])
            
            # Crear instancia del modelo SQLAlchemy
            db_project = Project(**model_data) 
            projects_to_add.append(db_project)
            # --------------------------------------------- #
            projects_created_count += 1
        else:
            logger.info(f"Proyecto con ID {project_id} ya existe, omitiendo creación.")
            
    # Añadir y hacer commit fuera del bucle si hay proyectos nuevos
    if projects_to_add:
        logger.info(f"Añadiendo {len(projects_to_add)} nuevos proyectos a la sesión...")
        db.add_all(projects_to_add)
        try:
            await db.commit()
            logger.info("Commit de nuevos proyectos realizado.")
            # Opcional: Refrescar si necesitas los objetos actualizados
            # for proj in projects_to_add:
            #     await db.refresh(proj)
        except Exception as e:
            logger.error(f"Error durante el commit de proyectos iniciales: {e}", exc_info=True)
            await db.rollback() # Revertir si falla el commit
            raise # Relanzar el error para que se vea en el lifespan
            
    logger.info(f"Se crearon {projects_created_count} nuevos proyectos.")

    # --- Poblar Posts del Blog ---
    logger.info("Verificando/poblando posts iniciales del blog...")
    posts_created_count = 0
    posts_to_add = [] # Lista para añadir en batch
    
    for post_data in initial_data.initial_blog_posts:
        post_id = post_data.get("id") # ID es string aquí
        if not post_id:
            logger.warning(f"Post en initial_data sin ID, omitiendo: {post_data.get('title')}")
            continue
        
        # Usar la función get_blog_post que ya existe (asume ID es int? Revisar modelo)
        # Necesitamos asegurar que el ID usado para la búsqueda coincida con el tipo de la PK del modelo
        # Leer modelo BlogPost para verificar tipo de PK (id)
        # *** ASUMIENDO que el modelo BlogPost tiene id como String PK ***
        # Si fuera int, necesitaríamos convertir post_id a int aquí.
        existing_post = await db.get(BlogPost, post_id) # Usar db.get directamente si PK es simple
        # O si get_blog_post espera int: await crud.blog.get_blog_post(db, blog_post_id=int(post_id)) 
        
        if not existing_post:
            logger.info(f"Preparando creación de post con ID: {post_id}")
            
            # Crear instancia del MODELO BlogPost directamente
            model_data = post_data.copy()
            
            # Asegurarse que 'date' es un objeto date/datetime compatible con SQLAlchemy
            # initial_data usa datetime.date, que debería ser compatible con SQLA Date
            if "date" in model_data and not isinstance(model_data["date"], date):
                 logger.warning(f"El campo 'date' para post {post_id} no es un objeto date: {type(model_data['date'])}. Intentando continuar.")
                 # Podríamos intentar convertirlo si es string: model_data["date"] = date.fromisoformat(model_data["date"])
            
            # Crear la instancia del modelo
            # Necesitamos añadir author_id si el modelo lo requiere y no está en initial_data
            # Por ahora, asumimos que no es estrictamente necesario aquí o se manejará con default
            # Si el modelo tiene author_id como obligatorio, esto fallará
            if "author_id" not in model_data:
                 model_data["author_id"] = 1 # O el ID del superusuario por defecto
                 logger.warning(f"Asignando author_id=1 por defecto al post {post_id}")
            
            # Crear instancia BlogPost
            try:
                 db_post = BlogPost(**model_data) 
                 posts_to_add.append(db_post)
                 posts_created_count += 1
            except Exception as e:
                 logger.error(f"Error al crear instancia del modelo BlogPost para ID {post_id}: {e}", exc_info=True)

        else:
            logger.info(f"Post con ID {post_id} ya existe, omitiendo creación.")

    # Añadir y hacer commit fuera del bucle si hay posts nuevos
    if posts_to_add:
        logger.info(f"Añadiendo {len(posts_to_add)} nuevos posts de blog a la sesión...")
        db.add_all(posts_to_add)
        try:
            await db.commit()
            logger.info("Commit de nuevos posts de blog realizado.")
        except Exception as e:
            logger.error(f"Error durante el commit de posts iniciales: {e}", exc_info=True)
            await db.rollback()
            raise
            
    logger.info(f"Se crearon {posts_created_count} nuevos posts de blog.")
    
    # --- Poblar otros datos si es necesario ---
    
    logger.info("Inicialización de la base de datos completada.") 