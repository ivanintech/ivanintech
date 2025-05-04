# ivanintech/backend/app/services/gemini_service.py
import google.generativeai as genai
import httpx # Para poder manejar errores HTTP específicos como 429
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from app.core.config import settings

logger = logging.getLogger(__name__)

# Configuración de Gemini (se asume que ya está configurado en aggregated_news_service o main)
# Si no, descomentar:
# if settings.GEMINI_API_KEY:
#     genai.configure(api_key=settings.GEMINI_API_KEY)
# else:
#     logger.warning("GEMINI_API_KEY not set. Enrichment will fail.")

def parse_json_safely(text: str) -> Optional[Dict[str, Any]]:
    """Attempts to extract and parse a JSON block from Gemini's response."""
    try:
        # Busca el inicio y fin del bloque JSON, ignorando ```json``` si existe
        text_cleaned = text.strip().removeprefix('```json').removesuffix('```').strip()
        json_start = text_cleaned.find('{')
        json_end = text_cleaned.rfind('}')
        if json_start != -1 and json_end != -1:
            json_str = text_cleaned[json_start:json_end+1]
            return json.loads(json_str)
        else:
            logger.warning(f"No JSON object found in Gemini response: {text[:100]}...")
            return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON from Gemini: {e}. Response: {text[:100]}...", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Unexpected error parsing Gemini JSON: {e}", exc_info=True)
        return None

async def enrich_news_with_gemini(
    title: str, 
    url: str, 
    description: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Enriches scraped news using the Gemini API.

    Args:
        title: The original title of the scraped article.
        url: The original URL of the scraped article.
        description: An optional short description or excerpt if available.

    Returns:
        A dictionary containing enriched data (title, description, imageUrl, 
        publishedAt, relevance_score, sectors) or None if enrichment fails.
        Raises httpx.HTTPStatusError if a specific HTTP error (like 429) occurs.
    """
    if not settings.GEMINI_API_KEY:
        logger.warning("Cannot enrich news: GEMINI_API_KEY is not configured.")
        return None

    # Construir el contenido base para el prompt
    content_to_process = f"Artículo Original:\nTítulo: {title}\nURL: {url}"
    if description:
        content_to_process += f"\nExtracto: {description[:500]}" # Limitar longitud

    # Prompt mejorado para Gemini
    # Usamos comillas triples estándar para cadenas multilínea
    prompt = f"""
    Eres un asistente experto en tecnología e inteligencia artificial. 
    Analiza el siguiente artículo scrapeado y genera un resumen conciso y atractivo para una sección de noticias. 
    Extrae información clave y devuélvela **SOLAMENTE** como un objeto JSON válido.

    {content_to_process}

    Basado en el título, URL y extracto (si está disponible), realiza las siguientes tareas:
    1.  **Genera un título nuevo y atractivo** (máximo 15 palabras) para la noticia, en español.
    2.  **Escribe una descripción concisa** (máximo 100 palabras) resumiendo los puntos clave del artículo, en español.
    3.  **Sugiere una URL de imagen relevante (imageUrl)** si puedes inferirla o encontrarla relacionada con el contenido (devuelve null si no es posible o relevante). NO inventes URLs.
    4.  **Estima una fecha de publicación (publishedAt)** en formato ISO 8601 UTC (YYYY-MM-DDTHH:MM:SSZ) si el contenido da pistas sobre la fecha. Si no, devuelve null.
    5.  **Evalúa la relevancia (relevance_score)** para un profesional interesado en IA/Tecnología, del 1 (baja) al 10 (alta).
    6.  **Identifica los sectores tecnológicos/económicos clave (sectors)** impactados o mencionados (máximo 5). Devuelve una lista de strings. Si no aplica, devuelve [].

    Formato JSON esperado:
    {{
      "title": "string",
      "description": "string",
      "imageUrl": "string_or_null",
      "publishedAt": "iso_string_or_null", 
      "relevance_score": integer,
      "sectors": ["string"] 
    }}

    IMPORTANTE: Responde **únicamente** con el objeto JSON, sin texto introductorio ni explicaciones adicionales.

    JSON:
    """

    try:
        # Usar el modelo gratuito o el configurado
        # Asegúrate que 'GEMINI_MODEL_NAME' esté definido en tus settings (config.py)
        # Si no, puedes hardcodearlo aquí temporalmente, ej: 'gemini-1.5-flash-latest'
        model_name = getattr(settings, 'GEMINI_MODEL_NAME', 'gemini-1.5-flash-latest') 
        model = genai.GenerativeModel(model_name)
        
        logger.info(f"Sending request to Gemini for: {title[:50]}...")
        
        # Usar generate_content_async para llamadas asíncronas
        response = await model.generate_content_async(prompt)
        
        # Parsear la respuesta JSON
        enriched_data = parse_json_safely(response.text)

        if not enriched_data:
            logger.warning(f"Gemini did not return valid JSON for: {title[:50]}")
            return None

        # Validaciones básicas del JSON recibido (opcional pero recomendado)
        if not isinstance(enriched_data.get("title"), str) or \
           not isinstance(enriched_data.get("description"), str) or \
           not isinstance(enriched_data.get("relevance_score"), int) or \
           not isinstance(enriched_data.get("sectors"), list):
            logger.warning(f"Gemini JSON structure is invalid for: {title[:50]}")
            return None
            
        # Convertir publishedAt a datetime si existe y es válida, si no, None
        published_at_str = enriched_data.get("publishedAt")
        published_at_dt = None
        if published_at_str:
            try:
                published_at_dt = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
                if published_at_dt.tzinfo is None:
                     published_at_dt = published_at_dt.replace(tzinfo=timezone.utc)
                enriched_data["publishedAt"] = published_at_dt # Reemplazar string con datetime
            except ValueError:
                 logger.warning(f"Gemini returned invalid publishedAt format: {published_at_str}")
                 enriched_data["publishedAt"] = None # Establecer a None si el formato es inválido
        else:
             enriched_data["publishedAt"] = None # Asegurar que sea None si Gemini devuelve null

        logger.info(f"Successfully enriched: {title[:50]}")
        return enriched_data

    except Exception as e:
        # Re-lanzar errores HTTP específicos para que la función llamante los maneje (ej. 429)
        if isinstance(e, httpx.HTTPStatusError):
             logger.error(f"HTTP Error {e.response.status_code} calling Gemini API for '{title[:50]}': {e}")
             raise e 
        # Loguear otros errores genéricos
        logger.error(f"Unexpected error calling Gemini API for '{title[:50]}': {e}", exc_info=True)
        return None 