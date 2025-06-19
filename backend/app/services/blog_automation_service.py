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
from app.crud import crud_news, crud_blog, crud_user

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
        gemini_model = None
except Exception as e:
    logger.error(f"Error configuring Gemini API client: {e}")
    gemini_model = None

async def get_promising_news_topic(db: AsyncSession) -> NewsItem | None:
    """Finds a recent, high-relevance news item to be used as a blog topic."""
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
        
        # Optional: Add logic to check if a blog post on this topic already exists
        logger.info(f"Found promising news topic: {news_items[0].title}")
        return news_items[0]
        
    except Exception as e:
        logger.error(f"Error fetching promising news topic: {e}", exc_info=True)
        return None

async def generate_blog_draft(news_item: NewsItem) -> tuple[str | None, str | None]:
    """Generates a blog post draft from a news item using the Gemini API."""
    if not gemini_model:
        logger.warning("Gemini model not available. Cannot generate blog draft.")
        return None, None
        
    logger.info(f"Generating blog draft for news: {news_item.title}")
    
    prompt = f"""
    You are an expert technology and blog writing AI assistant.
    
    Task: Write a 300-500 word blog post draft based on the following AI news. The tone should be informative yet accessible for technology enthusiasts.

    News Item:
    Title: {news_item.title}
    Description: {news_item.description}
    Source: {news_item.sourceName}
    Original Link: {news_item.url}

    Instructions:
    1. Create an engaging and concise title for the blog post (do NOT use the word "draft").
    2. Summarize the key points of the news item.
    3. Add a brief analysis of the importance or potential implications of this news in the field of AI or technology.
    4. Keep the language clear and avoid overly technical jargon.
    5. Structure the text in short paragraphs.
    6. End with a brief conclusion or an open-ended question to encourage reflection.
    7. Respond ONLY with the title and the blog content, separated by "---CONTENT---". Example: 
       Engaging Title
       ---CONTENT---
       This is the first paragraph of the blog...
       This is the second paragraph...
    """
    
    try:
        generation_config = genai.types.GenerationConfig(
            temperature=0.7, # Controls randomness
        )
        response = await gemini_model.generate_content_async(
            prompt,
            generation_config=generation_config
        )
        
        if response.parts:
            generated_text = response.text
            parts = generated_text.split("---CONTENT---", 1)
            if len(parts) == 2:
                generated_title = parts[0].strip()
                generated_content = parts[1].strip()
                logger.info(f"Successfully generated draft content for: {generated_title}")
                return generated_title, generated_content
            else:
                logger.warning("Gemini response did not contain the expected separator. Using full response as content.")
                return f"Analysis: {news_item.title}", generated_text.strip()
        else:
             logger.warning("Gemini response did not contain any parts.")
             if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                logger.warning(f"Prompt Feedback: {response.prompt_feedback}")
             return None, None

    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}", exc_info=True)
        return None, None

async def get_default_author_id(db: AsyncSession) -> int | None:
    """Gets the ID of the first available superuser to assign as author."""
    logger.info("Getting default author ID (first superuser)...")
    try:
        superuser = await crud_user.user.get_first_superuser(db)
        if superuser:
            logger.info(f"Found default superuser ID: {superuser.id}")
            return superuser.id
        else:
            logger.warning("No active superuser found in the database.")
            return None
    except Exception as e:
        logger.error(f"Error fetching default superuser: {e}", exc_info=True)
        return None

async def create_blog_draft(db: AsyncSession, title: str, content: str, author_id: int, linkedin_url: str | None) -> BlogPost | None:
    """Creates and saves a blog post with 'draft' status."""
    logger.info(f"Creating blog draft with title: {title}")

    # The slug will be generated automatically by the CRUD layer to ensure uniqueness.
    blog_post_in = BlogPostCreate(
        title=title,
        content=content,
        status='draft', # Explicitly set status to draft
        linkedin_post_url=linkedin_url
    )
    try:
        # The CRUD function now handles slug generation and uniqueness.
        created_post = await crud_blog.create_blog_post(db=db, blog_post_in=blog_post_in, author_id=author_id)
        logger.info(f"Successfully created blog draft with ID: {created_post.id}")
        return created_post
    except Exception as e:
        # The CRUD layer will raise an exception on commit failure, which we catch here.
        logger.error(f"Error creating blog draft in DB for title '{title}': {e}", exc_info=True)
        return None

async def run_blog_draft_generation(db: AsyncSession):
    """Main orchestrator function for the blog draft generation process."""
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

    await create_blog_draft(
        db, 
        title=generated_title, 
        content=generated_content, 
        author_id=author_id,
        linkedin_url=news_topic.url # Pasamos la URL de la noticia original
    )
    logger.info("Blog draft generation process finished successfully.") 