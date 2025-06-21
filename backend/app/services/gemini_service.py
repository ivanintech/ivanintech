# ivanintech/backend/app/services/gemini_service.py
import google.generativeai as genai
import httpx # To get the content of the URL if necessary
import json
import logging
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timezone
from bs4 import BeautifulSoup # To parse HTML if necessary
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core.exceptions import ResourceExhausted
import trafilatura
# Importar multiprocessing y la API síncrona de Playwright
import asyncio
import multiprocessing
from queue import Empty as QueueEmpty
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from app.core.config import settings
from app.services import youtube_service

logger = logging.getLogger(__name__)

# Configurar el API Key de Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY is not configured. Gemini service will not work.")


# --- Función de Extracción de Playwright para Ejecución en Proceso Separado ---
# Esta función DEBE estar a nivel de módulo para que multiprocessing pueda "picklearla".
def playwright_extractor_process(url: str, result_queue: multiprocessing.Queue):
    """
    Ejecuta Playwright en un proceso completamente separado para evitar conflictos
    de bucles de eventos asyncio en Windows con Uvicorn.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            try:
                page.goto(url, wait_until="networkidle", timeout=35000)
                html_content = page.content()
            finally:
                browser.close()
        
        text_content = trafilatura.extract(html_content, include_comments=False, include_tables=False)
        
        if not text_content:
            print(f"WARNING: Playwright (process) extracted HTML but Trafilatura found no content for {url}.")
            result_queue.put(None)
            return

        print(f"INFO: Successfully extracted content from {url} using Playwright process fallback.")
        result_queue.put(text_content[:25000])

    except Exception as e:
        # El logging tradicional es complicado entre procesos; print es más robusto para diagnóstico.
        print(f"ERROR: An unexpected error occurred in Playwright process for {url}: {e}")
        result_queue.put(None)


class GeminiService:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured. Gemini service cannot be initialized.")
        self.model = genai.GenerativeModel("gemini-1.5-flash-latest")

    async def _get_content_with_playwright_process(self, url: str) -> Optional[str]:
        """
        Orquesta la ejecución del extractor de Playwright en un proceso separado.
        """
        # Usamos el contexto "spawn" que es el por defecto en Windows y el más seguro en otros SO.
        ctx = multiprocessing.get_context("spawn")
        result_queue = ctx.Queue()
        
        process = ctx.Process(
            target=playwright_extractor_process,
            args=(url, result_queue)
        )

        try:
            process.start()
            # .get() es bloqueante, así que lo ejecutamos en un hilo para no congelar el loop de FastAPI.
            # Añadimos un timeout para no esperar indefinidamente.
            content = await asyncio.to_thread(result_queue.get, timeout=45)
            return content
        except QueueEmpty:
            logger.error(f"Playwright process timed out after 45s for URL {url}")
            return None
        except Exception as e:
            logger.error(f"Error orchestrating Playwright process for {url}: {e}", exc_info=True)
            return None
        finally:
            # Nos aseguramos de que el proceso termine.
            if process.is_alive():
                process.terminate()
            process.join() # Esperamos a que el proceso termine de limpiar.


    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(ResourceExhausted)
    )
    async def get_content_from_url(self, url: str) -> Optional[str]:
        """
        Obtiene el contenido de una URL con un enfoque de múltiples capas.
        1. Intento rápido con httpx.
        2. Fallback a renderizado de navegador completo con Playwright en un PROCESO separado.
        """
        # 1. Intento Rápido con HTTPX
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                html_content = response.text
            
            text_content = trafilatura.extract(html_content, include_comments=False, include_tables=False, no_fallback=True)
            
            if text_content:
                logger.info(f"Successfully extracted content from {url} using fast method.")
                return text_content[:25000]

        except httpx.RequestError as e:
            logger.warning(f"Fast method request error for {url}: {e}. Proceeding to browser fallback.")
        except Exception as e:
            logger.warning(f"Fast method failed for {url}: {e}. Proceeding to browser fallback.")

        # 2. Fallback a Playwright en un proceso separado
        logger.info(f"Fast method failed for {url}, falling back to Playwright in a separate process.")
        return await self._get_content_with_playwright_process(url)

    async def evaluate_and_summarize_content(self, content: str, is_resource: bool, user_prompt: str) -> Optional[Dict[str, Any]]:
        """
        Evalúa contenido y extrae detalles usando Gemini.
        """
        if not content:
            return None

        prompt_parts = [
            "You are an expert AI and technology analyst for the ivanintech.com blog.",
            f"Context: {user_prompt}",
            "Analyze the following text content:",
            "---",
            content,
            "---",
            "Based on the text, provide the following details in JSON format:",
            "1. `title`: A concise and engaging title (max 15 words).",
            "2. `summary`: A brief summary (2-4 sentences).",
            "3. `relevance_rating`: A float from 0.0 to 5.0 indicating relevance to AI/software development. 5.0 is highly relevant.",
            "4. `tags`: A list of 2-5 relevant lowercase tags (e.g., [\"python\", \"ai\"]).",
        ]
        
        if is_resource:
            prompt_parts.append("5. `resource_type`: The type of resource (e.g., Video, Article, GitHub, Tool, Course).")

        prompt_parts.append("Return ONLY a valid JSON object with these keys.")
        
        complete_prompt = "\\n".join(prompt_parts)
        
        try:
            response = await self.model.generate_content_async(complete_prompt)
            cleaned_response_text = response.text.strip()
            if cleaned_response_text.startswith('```json'):
                cleaned_response_text = cleaned_response_text[7:]
            if cleaned_response_text.endswith('```'):
                cleaned_response_text = cleaned_response_text[:-3]
            
            return json.loads(cleaned_response_text)
        except (json.JSONDecodeError, AttributeError, ValueError) as e:
            logger.error(f"Failed to decode Gemini JSON response. Text: '{response.text}'. Error: {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred calling Gemini: {e}", exc_info=True)
            # No relanzamos aquí para permitir que la función que llama maneje el None
            return None
            
# El resto del fichero (ExtractedContent, get_content_from_url, etc.) que no pertenece
# a la clase GeminiService puede ser eliminado si ya no se usa directamente, o mantenido si
# otras partes del código dependen de ello. En este refactor, la lógica principal de
# extracción se ha movido DENTRO de la clase GeminiService.

class ExtractedContent(BaseModel):
    text: Optional[str] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    og_type: Optional[str] = None
    # New field for the best image found by our logic
    best_image_url: Optional[str] = None

async def get_content_from_url(url: str) -> ExtractedContent:
    """
    DEPRECATED: This function's logic has been moved into the GeminiService
    for better integration with the multi-layered fetching strategy.
    Keeping it for now to avoid breaking other potential dependencies.
    """
    logger.warning("DEPRECATION WARNING: Standalone 'get_content_from_url' is deprecated. Use GeminiService instance.")
    
    extracted = ExtractedContent()
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, verify=False) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract OpenGraph Metadata
        extracted.og_title = soup.find("meta", property="og:title")["content"] if soup.find("meta", property="og:title") else None
        extracted.og_description = soup.find("meta", property="og:description")["content"] if soup.find("meta", property="og:description") else None
        extracted.og_image = soup.find("meta", property="og:image")["content"] if soup.find("meta", property="og:image") else None
        extracted.og_type = soup.find("meta", property="og:type")["content"] if soup.find("meta", property="og:type") else None
        
        # --- Improved Thumbnail Logic ---
        best_image_found = None
        # 1. Priority: og:image if it exists
        if extracted.og_image:
            best_image_found = extracted.og_image

        # 2. YouTube-specific logic
        elif "youtube.com" in url or "youtu.be" in url:
            video_id = None
            if "watch?v=" in url:
                video_id = url.split("watch?v=")[1].split("&")[0]
            elif "youtu.be/" in url:
                video_id = url.split("youtu.be/")[1].split("?")[0]
            
            if video_id:
                # We use the high-quality thumbnail for videos
                best_image_found = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
            else:
                # For channels, the og:image (already checked) is usually the avatar, which is sufficient.
                pass

        # 3. Amazon-specific logic (example for books)
        elif "amazon." in url:
            img_tag = soup.select_one("#img-canvas img, #landingImage, #ebooks-img-canvas img")
            if img_tag and img_tag.get('src'):
                best_image_found = img_tag.get('src')

        # 4. Generic logic: find the largest image (if nothing has been found yet)
        if not best_image_found:
            largest_image = None
            max_area = 0
            for img in soup.find_all('img'):
                try:
                    width = int(img.get('width', 0))
                    height = int(img.get('height', 0))
                    area = width * height
                    if area > max_area:
                        max_area = area
                        largest_image = img.get('src')
                except (ValueError, TypeError):
                    continue
            if largest_image:
                 best_image_found = largest_image

        extracted.best_image_url = best_image_found
        
        for script_or_style in soup(["script", "style", "header", "footer", "nav", "aside"]):
            script_or_style.decompose()
        
        main_content_tags = ['main', 'article', 'div[role="main"]', 'div[class*="content"]', 'div[id*="content"]']
        text_content = None
        for tag_selector in main_content_tags:
            try:
                element = soup.select_one(tag_selector)
                if element:
                    text_content = element.get_text(separator='\\n', strip=True)
                    break
            except Exception as e:
                logger.warning(f"Selector '{tag_selector}' failed for URL {url}: {e}")
                continue
        
        if not text_content:
            body = soup.find('body')
            if body:
                text_content = body.get_text(separator='\\n', strip=True)
        else:
                text_content = response.text
        
        max_length = 18000
        extracted.text = text_content[:max_length] if text_content else None
        logger.debug(f"Content extracted from {url}: OG Title: {extracted.og_title}, Best Image: {extracted.best_image_url}")
        return extracted

    except httpx.RequestError as e:
        logger.error(f"Network error while accessing URL {url}: {e}")
        return extracted
    except Exception as e:
        logger.error(f"Error extracting text/OG from URL {url}: {e}", exc_info=True)
        return extracted

async def generate_resource_details(
    url: str, 
    user_title: Optional[str] = None,
    user_personal_note: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Orchestrates fetching content and generating details using the GeminiService class.
    This acts as a high-level entry point.
    """
    gemini = GeminiService()

    # 1. Get content using the robust, multi-layered method
    content = await gemini.get_content_from_url(url)
    if not content:
        logger.error(f"Failed to retrieve content from URL: {url}")
        raise ValueError("Could not retrieve content from the URL.")

    # 2. Build the user prompt
    user_prompts = ["Evaluate this resource for its relevance to AI, software development, and technology."]
    if user_title:
        user_prompts.append(f"The user suggests the title: '{user_title}'.")
    if user_personal_note:
        user_prompts.append(f"The user added a personal note: '{user_personal_note}'.")
    user_prompt = " ".join(user_prompts)
    
    # 3. Analyze content with Gemini
    try:
        details = await gemini.evaluate_and_summarize_content(
            content=content,
            is_resource=True,
            user_prompt=user_prompt
        )

        if not details or details.get('relevance_rating', 0) < 2.0:
            logger.warning(f"URL {url} deemed not relevant or analysis failed.")
            raise ValueError("The content of the URL is not considered relevant to AI or could not be analyzed.")

        # Aquí podrías añadir lógica adicional para el thumbnail si es necesario
        # Por ahora, nos enfocamos en el refactor.
        
        return details

    except Exception as e:
        logger.error(f"Error during Gemini analysis for {url}: {e}", exc_info=True)
        # Relanzamos la excepción para que el endpoint la maneje como un 503.
        raise e

async def generate_and_tag_news_from_content(
    title: str,
    content: Optional[str]
) -> Optional[Dict[str, Any]]:
    if not settings.GEMINI_API_KEY:
        logger.error("Gemini service is not configured.")
        return None

    if not content:
        logger.warning(f"No content provided for article '{title}'. Skipping Gemini analysis.")
        return {"relevance_rating": 0, "tags": [], "summary": "Content was not available for analysis."}
    
    prompt = f"""
    You are an expert AI and technology analyst for the ivanintech.com blog.
    Your task is to evaluate a news article based on its title and content.
    
    Title: "{title}"
    Content:
    ---
    {content[:15000]}
    ---
    
    Provide the following details in a single, valid JSON object and nothing else:
    1. "relevance_rating": A float from 0.0 to 5.0. A score of 5.0 means it is extremely relevant and interesting for an audience of AI professionals, software developers, and tech entrepreneurs. A score below 2.5 is not relevant.
    2. "tags": A JSON list of 2 to 4 relevant lowercase keyword tags for the article (e.g., ["ai", "startup", "ethics"]).
    3. "summary": A concise, neutral, one-paragraph summary of the article (3-5 sentences).
    
    Return ONLY the JSON object.
    """
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = await model.generate_content_async(prompt)
        
        # Robust JSON cleaning
        cleaned_response_text = response.text.strip()
        if cleaned_response_text.startswith('```json'):
            cleaned_response_text = cleaned_response_text[7:]
        if cleaned_response_text.endswith('```'):
            cleaned_response_text = cleaned_response_text[:-3]

        return json.loads(cleaned_response_text)
    
    except (json.JSONDecodeError, AttributeError, ValueError) as e:
        logger.error(f"Failed to decode Gemini JSON response for article '{title}'. Text: '{response.text if 'response' in locals() else 'N/A'}'. Error: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred calling Gemini for article '{title}': {e}", exc_info=True)
        return None 