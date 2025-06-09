# ivanintech/backend/app/services/gemini_service.py
import google.generativeai as genai
import httpx # Para obtener el contenido de la URL si es necesario
import json
import logging
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timezone
from bs4 import BeautifulSoup # Para parsear HTML si es necesario
from pydantic import BaseModel

from app.core.config import settings

logger = logging.getLogger(__name__)

# Configurar la API Key de Gemini al iniciar el módulo
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY no está configurada. El servicio Gemini no funcionará.")

class ExtractedContent(BaseModel):
    text: Optional[str] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    og_type: Optional[str] = None # e.g., article, video.website

def get_content_from_url(url: str) -> ExtractedContent:
    """Obtiene el contenido textual principal y metadatos OpenGraph de una URL."""
    extracted = ExtractedContent()
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        with httpx.Client(timeout=15.0, follow_redirects=True, verify=False) as client: # verify=False es para evitar errores SSL en algunos sitios, usar con precaución
            response = client.get(url, headers=headers)
            response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extraer Metadatos OpenGraph
        extracted.og_title = soup.find("meta", property="og:title")["content"] if soup.find("meta", property="og:title") else None
        extracted.og_description = soup.find("meta", property="og:description")["content"] if soup.find("meta", property="og:description") else None
        extracted.og_image = soup.find("meta", property="og:image")["content"] if soup.find("meta", property="og:image") else None
        extracted.og_type = soup.find("meta", property="og:type")["content"] if soup.find("meta", property="og:type") else None
        
        for script_or_style in soup(["script", "style", "header", "footer", "nav", "aside"]):
            script_or_style.decompose()
        
        main_content_tags = ['main', 'article', 'div[role="main"]', 'div[class*="content"]_value', 'div[id*="content"]_value']
        text_content = None
        for tag_selector in main_content_tags:
            element = soup.select_one(tag_selector)
            if element:
                text_content = element.get_text(separator='\n', strip=True)
                break
        
        if not text_content:
            body = soup.find('body')
            if body:
                text_content = body.get_text(separator='\n', strip=True)
        else:
                text_content = response.text # Fallback al texto plano si todo falla
        
        max_length = 18000 # Límite generoso para Gemini 1.5 Flash (context window mayor)
        extracted.text = text_content[:max_length] if text_content else None
        logger.debug(f"Contenido extraído de {url}: OG Title: {extracted.og_title}, Texto (primeros 100 chars): {extracted.text[:100] if extracted.text else 'N/A'}")
        return extracted

    except httpx.RequestError as e:
        logger.error(f"Error de red al acceder a la URL {url}: {e}")
        return extracted # Devuelve lo que se haya podido extraer
    except Exception as e:
        logger.error(f"Error extrayendo texto/OG de la URL {url}: {e}", exc_info=True)
        return extracted # Devuelve lo que se haya podido extraer

async def generate_resource_details(
    url: str, 
    user_title: Optional[str] = None,
    user_personal_note: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    if not settings.GEMINI_API_KEY:
        logger.error("El servicio Gemini no está configurado.")
        return None
    try:
        # Chequeo rápido si el modelo está disponible (puede lanzar error si no)
        genai.get_model("models/gemini-1.5-flash-latest") 
    except Exception as e:
        logger.error(f"Error al obtener modelo de Gemini: {e}")
        return None

    extracted_data = get_content_from_url(url)
    
    text_for_prompt = extracted_data.text
    if not text_for_prompt:
        logger.warning(f"No se pudo extraer contenido textual de la URL: {url}. Se intentará generar detalles solo con la URL y metadatos OG.")
        text_for_prompt = f"Análisis del recurso en la URL: {url}. Título OpenGraph: {extracted_data.og_title or 'N/A'}. Descripción OpenGraph: {extracted_data.og_description or 'N/A'}."
    
    # Priorizar título de OG si existe y el usuario no dio uno
    effective_title_for_prompt = user_title or extracted_data.og_title

    model = genai.GenerativeModel("gemini-1.5-flash-latest")

    prompt_parts = [
        f"Eres un asistente experto en tecnología e IA para el blog ivanintech.com. Analiza el siguiente recurso web y genera detalles en formato JSON.",
        f"URL del recurso: {url}",
    ]
    if effective_title_for_prompt:
        prompt_parts.append(f"Título conocido (usuario/OpenGraph): {effective_title_for_prompt}")
    if extracted_data.og_description:
        prompt_parts.append(f"Descripción OpenGraph: {extracted_data.og_description}")
    if extracted_data.og_type:
        prompt_parts.append(f"Tipo OpenGraph: {extracted_data.og_type}")
    
    prompt_parts.extend([
        "Contenido textual principal extraído del recurso (primeras ~18000 caracteres):\n---\n",
        text_for_prompt,
        "\n---",
        "Considerando toda la información (URL, metadatos OpenGraph si los hay, y el contenido textual), genera lo siguiente:",
        "1. `title`: Un título conciso y atractivo (máx 15 palabras). Mejora el título conocido si es posible, o crea uno si no hay.",
        "2. `ai_generated_description`: Una descripción breve (2-4 frases) sobre el recurso, útil e interesante.",
        "3. `personal_note`: Una 'nota personal' (1-2 frases, humanizada, como si yo, Iván, lo recomendara).",
        "4. `resource_type`: Un tipo de recurso (ej: Video, Artículo, GitHub, Documentación, Herramienta, Curso, Podcast, Noticia). Infiere del tipo OG si es útil.",
        "5. `tags`: Lista de 2-5 etiquetas relevantes (strings, ej: [\"python\", \"IA\"]).",
        "6. `thumbnail_url_suggestion`: Sugiere una URL directa a una imagen de vista previa o logo. Prioriza la `og:image` si existe y es válida ({extracted_data.og_image or 'N/A'}). Si no, intenta inferir una. Devuelve null si no.",
        "Devuelve ÚNICAMENTE un objeto JSON válido con estas claves. Asegúrate de que esté bien formado."
    ])

    if user_personal_note:
        prompt_parts.insert(len(prompt_parts) - 3, f"Nota personal proporcionada por el usuario (puedes usarla como inspiración): {user_personal_note}")
    
    complete_prompt = "\n".join(prompt_parts)
    logger.debug(f"Enviando prompt a Gemini para URL {url}:\n{complete_prompt[:1000]}...") # Loguear solo una parte del prompt

    try:
        response = await model.generate_content_async(complete_prompt)
        cleaned_response_text = response.text.strip()
        if cleaned_response_text.startswith("```json"):
            cleaned_response_text = cleaned_response_text[7:]
        if cleaned_response_text.endswith("```"):
            cleaned_response_text = cleaned_response_text[:-3]
        
        logger.debug(f"Respuesta de Gemini (texto limpio): {cleaned_response_text}")
        details = json.loads(cleaned_response_text)
        
        final_details = {
            "title": details.get("title"),
            "ai_generated_description": details.get("ai_generated_description"),
            "personal_note": details.get("personal_note"),
            "resource_type": details.get("resource_type"),
            "tags": details.get("tags"),
            "thumbnail_url_suggestion": details.get("thumbnail_url_suggestion") or extracted_data.og_image # Usar og_image como fallback si Gemini no sugiere nada
        }
        
        logger.info(f"Detalles generados por Gemini para {url}: {final_details}")
        return final_details
    except json.JSONDecodeError as e:
        logger.error(f"Error decodificando JSON de Gemini para {url}. Respuesta: \n{response.text}\nError: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Error llamando a la API de Gemini para {url}: {e}", exc_info=True)
        return None 

# Este archivo contendrá la lógica para interactuar con la API de Gemini. 