import google.generativeai as genai
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from datetime import datetime, timedelta

from app.core.config import settings
from app.db.models.news_item import NewsItem
from app.db.models.blog_post import BlogPost
from app.db.models.user import User
from app.schemas.blog import BlogPostCreate
from app.crud import crud_news, crud_blog, crud_user # Assuming crud_user exists or will be created

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini client
try:
    if settings.GEMINI_API_KEY:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        logger.info("Gemini API client configured successfully.")
        # Define the model to use
        gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')
    else:
        logger.warning("GEMINI_API_KEY not found in settings. Blog draft generation will be disabled.")
        genai = None
        gemini_model = None
except Exception as e:
    logger.error(f"Error configuring Gemini API client: {e}")
    genai = None
    gemini_model = None

# Placeholder functions - will be implemented next
async def get_promising_news_topic(db: AsyncSession) -> NewsItem | None:
    logger.info("Searching for a promising news topic...")
    try:
        # Look for news in the last 48 hours with the highest relevance score
        forty_eight_hours_ago = datetime.utcnow() - timedelta(hours=48)
        news_items = await crud_news.get_news_items(
            db,
            sort_by="relevance_score",
            sort_order="desc",
            min_published_date=forty_eight_hours_ago,
            limit=5 # Get top 5 relevant news
        )
        
        if not news_items:
            logger.info("No recent relevant news found.")
            return None
        
        # Optional: Add logic here to check if a blog post based on these titles/slugs already exists
        # For now, just return the most relevant one
        logger.info(f"Found promising news topic: {news_items[0].title}")
        return news_items[0]
        
    except Exception as e:
        logger.error(f"Error fetching promising news topic: {e}")
        return None

async def generate_blog_draft(news_item: NewsItem) -> tuple[str | None, str | None]:
    if not gemini_model:
        logger.warning("Gemini model not available. Cannot generate blog draft.")
        return None, None
        
    logger.info(f"Generating blog draft for news: {news_item.title}")
    
    prompt = f"""
    Eres un asistente de IA experto en tecnología y redacción de blogs en español.
    
    Tarea: Escribe un borrador de entrada de blog de 300-500 palabras basado en la siguiente noticia de IA. El tono debe ser informativo pero accesible para entusiastas de la tecnología. 

    Noticia:
    Título: {news_item.title}
    Descripción: {news_item.description}
    Fuente: {news_item.source_name}
    Enlace original: {news_item.link}

    Instrucciones:
    1. Crea un título atractivo y conciso para la entrada del blog (NO uses la palabra "borrador" o "draft").
    2. Resume los puntos clave de la noticia.
    3. Añade un breve análisis sobre la importancia o las posibles implicaciones de esta noticia en el campo de la IA o la tecnología.
    4. Mantén un lenguaje claro y evita la jerga excesivamente técnica.
    5. Estructura el texto en párrafos cortos.
    6. Finaliza con una breve conclusión o una pregunta abierta para fomentar la reflexión.
    7. Responde únicamente con el título y el contenido del blog, separados por "---CONTENIDO---". Ejemplo: 
       Título Atractivo
       ---CONTENIDO---
       Este es el primer párrafo del blog...
       Este es el segundo párrafo...
    """
    
    try:
        generation_config = genai.types.GenerationConfig(
            temperature=0.7, # Controls randomness
            # max_output_tokens=800, # Optional limit
        )
        response = await gemini_model.generate_content_async(
            prompt,
            generation_config=generation_config
        )
        
        # Check for safety ratings or blocks if necessary
        # print(response.prompt_feedback)
        
        if response.parts:
            generated_text = response.text
            # Split the response into title and content
            parts = generated_text.split("---CONTENIDO---", 1)
            if len(parts) == 2:
                generated_title = parts[0].strip()
                generated_content = parts[1].strip()
                logger.info(f"Successfully generated draft content for: {generated_title}")
                return generated_title, generated_content
            else:
                logger.warning("Gemini response did not contain the expected separator. Using full response as content.")
                # Fallback: use the original news title and the full response as content
                return f"Análisis: {news_item.title}", generated_text.strip()
        else:
             logger.warning("Gemini response did not contain any parts.")
             # Consider checking response.prompt_feedback for block reasons
             if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                logger.warning(f"Prompt Feedback: {response.prompt_feedback}")
             return None, None

    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}")
        return None, None

async def get_default_author_id(db: AsyncSession) -> int | None:
    logger.info("Getting default author ID (first superuser)...")
    try:
        superuser = await crud_user.get_first_superuser(db)
        if superuser:
            logger.info(f"Found default superuser ID: {superuser.id}")
            return superuser.id
        else:
            logger.warning("No active superuser found in the database.")
            return None
    except Exception as e:
        logger.error(f"Error fetching default superuser: {e}")
        return None

async def create_blog_draft(db: AsyncSession, title: str, content: str, author_id: int) -> BlogPost | None:
    logger.info(f"Creating blog draft with title: {title}")
    # Generate slug (basic version, ensure it's unique)
    base_slug = title.lower().replace(' ', '-').encode('ascii', 'ignore').decode('ascii')
    base_slug = ''.join(c for c in base_slug if c.isalnum() or c == '-').strip('-')[:80]
    
    slug = base_slug
    counter = 1
    while True:
        existing_post = await crud_blog.get_blog_post_by_slug(db, slug=slug)
        if not existing_post:
            break
        slug = f"{base_slug}-{counter}"
        counter += 1
        if counter > 10: # Safety break
             logger.error(f"Could not generate unique slug for title: {title}")
             return None 

    blog_post_in = BlogPostCreate(
        title=title,
        slug=slug,
        content=content,
        status='draft' # Explicitly set status to draft
        # linkedin_post_url etc. will be None/default
    )
    try:
        created_post = await crud_blog.create_blog_post(db=db, blog_post_in=blog_post_in, author_id=author_id)
        logger.info(f"Successfully created blog draft with ID: {created_post.id}")
        return created_post
    except Exception as e:
        logger.error(f"Error creating blog draft in DB: {e}")
        # Consider rolling back transaction if needed, although commit is in crud
        return None

async def run_blog_draft_generation(db: AsyncSession):
    logger.info("Starting blog draft generation process...")
    if not gemini_model:
        logger.warning("Aborting blog draft generation: Gemini client not available.")
        return

    news_topic = await get_promising_news_topic(db)
    if not news_topic:
        logger.info("No suitable news topic found for blog draft generation.")
        return

    generated_title, generated_content = await generate_blog_draft(news_topic)
    if not generated_title or not generated_content:
        logger.warning("Failed to generate blog draft content from Gemini.")
        return

    author_id = await get_default_author_id(db)
    if not author_id:
        logger.error("Could not find a default author (superuser) ID to assign the draft.")
        return

    await create_blog_draft(db, title=generated_title, content=generated_content, author_id=author_id)
    logger.info("Blog draft generation process finished successfully.") 