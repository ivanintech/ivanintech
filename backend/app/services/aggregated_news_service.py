# ivanintech/backend/app/services/aggregated_news_service.py

import asyncio
import json
import httpx
import google.generativeai as genai
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError # Importar para manejo de errores
from datetime import datetime, timedelta, timezone, date # Añadir date
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse # Para validar URLs
from bs4 import BeautifulSoup
import logging # Añadir logging

from app.core.config import settings
# Importamos directamente la función create_news_item de crud_news
# en lugar de todo el módulo, para evitar confusión con otras funciones crud.
# Ya no es necesario, crearemos los objetos directamente aquí.
# from app.crud.crud_news import create_news_item 
from app.schemas.news import NewsItemCreate # Schema para crear/validar
from app.db.models import NewsItem # Modelo para consultar URLs existentes
from sqlalchemy.future import select
from app.db.session import get_db # <- CORRECCIÓN: Nombre correcto de la función
from app.crud.news import get_news_item_by_url, create_news_item # Importar funciones directamente
from app.services.gemini_service import enrich_news_with_gemini # Asumiendo que existe este servicio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    print("Gemini API Key configurada.")
else:
    print("Advertencia: GEMINI_API_KEY no está configurada. El análisis de noticias no funcionará.")

# Cliente HTTP asíncrono (reutilizable)
http_client = httpx.AsyncClient(timeout=20.0) 

# Constantes para APIs (asegúrate de que están en config.py o .env)
NEWSAPI_API_KEY = settings.NEWSAPI_API_KEY
GNEWS_API_KEY = settings.GNEWS_API_KEY
CURRENTS_API_KEY = settings.CURRENTS_API_KEY
MEDIASTACK_API_KEY = settings.MEDIASTACK_API_KEY
# APITUBE_API_KEY = settings.APITUBE_API_KEY # Comentado si no se usa

# --- Funciones Helper --- #

def is_valid_url(url: Optional[str]) -> bool:
    """Check if the URL is valid and uses http or https scheme."""
    if not url:
        return False
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except ValueError:
        return False

def parse_datetime_flexible(date_str: Optional[str]) -> Optional[datetime]:
    """Intenta parsear fechas en varios formatos ISO comunes, devolviendo None si falla."""
    if not date_str:
        return None
    # Formatos comunes a probar
    formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",  # Con milisegundos y Z
        "%Y-%m-%dT%H:%M:%SZ",    # Sin milisegundos y Z
        "%Y-%m-%d %H:%M:%S",     # Formato Currents API
        "%Y-%m-%dT%H:%M:%S",     # ISO sin offset
        "%Y-%m-%dT%H:%M:%S%z",   # ISO con offset +/-HHMM
        "%Y-%m-%dT%H:%M:%S%Z",   # ISO con nombre de zona (menos fiable)
    ]
    # Intentar parsear con zona horaria UTC si es posible
    try:
        # Reemplazar 'Z' si existe
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        # Si no tiene timezone, asumimos UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        # Intentar con formatos explícitos si fromisoformat falla
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                 # Si no tiene timezone, asumimos UTC
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                continue
    print(f"Advertencia: No se pudo parsear la fecha: {date_str}")
    return None # Devolver None si ningún formato funciona

# --- Funciones de Scraping ---

async def scrape_towards_data_science(http_client: httpx.AsyncClient) -> List[Dict[str, str]]:
    """Scrapes the latest articles from Towards Data Science."""
    url = "https://towardsdatascience.com/latest" # O la URL que consideremos más apropiada
    articles_found = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = await http_client.get(url, headers=headers, timeout=20.0) # Añadir cabecera User-Agent
        response.raise_for_status() # Lanza excepción para errores HTTP 4xx/5xx

        soup = BeautifulSoup(response.text, 'html.parser')

        # --- Lógica de Scraping (¡¡ESTO ES UN EJEMPLO Y NECESITA AJUSTE!!) ---
        # Inspecciona la web real de TDS para encontrar los selectores correctos.
        # Puede que necesites buscar contenedores, luego elementos 'a' con 'href', etc.
        # Ejemplo hipotético:
        # article_elements = soup.find_all('div', class_='postArticle') # Ajustar selector
        # Limitador simple para no procesar demasiados artículos
        limit = 10 
        count = 0

        # Ejemplo más realista basado en la estructura común de Medium/TDS:
        # Busca secciones principales, luego artículos dentro de ellas.
        main_content = soup.find('div', role='main')
        if not main_content:
             logger.warning("No main content found on Towards Data Science.")
             return []

        # Intenta encontrar artículos (esto puede variar mucho)
        possible_article_links = main_content.find_all('a', href=True)

        processed_urls = set() # Para evitar duplicados de la misma página

        for link in possible_article_links:
            href = link['href']
            # Filtrar enlaces internos de navegación, perfiles, etc. y asegurar URL completa
            if href.startswith('/') and not href.startswith('//') and len(href) > 50: # Heurística simple, mejorar
                full_url = f"https://towardsdatascience.com{href}"
                 # Evitar URLs ya procesadas y URLs que no parezcan artículos
                if full_url not in processed_urls and '/@' not in full_url and '/m/' not in full_url:
                    # Intentar obtener el título del texto del enlace o un h cercano
                    title_element = link.find(['h1', 'h2', 'h3', 'h4'])
                    title = title_element.text.strip() if title_element else link.text.strip()

                    # Aceptar solo si parece tener un título razonable
                    if title and len(title) > 10 and "member only" not in title.lower(): 
                        articles_found.append({"title": title, "url": full_url})
                        processed_urls.add(full_url)
                        count += 1
                        if count >= limit:
                            break # Salir si alcanzamos el límite

        # --- Fin Lógica de Scraping Ejemplo ---
        if not articles_found:
            logger.warning("No article links found matching the pattern on Towards Data Science.")

        logger.info(f"Scraped {len(articles_found)} potential articles from Towards Data Science.")
        return articles_found

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error scraping Towards Data Science: {e.response.status_code} - {e.request.url}")
    except httpx.RequestError as e:
        logger.error(f"Network error scraping Towards Data Science: {e}")
    except Exception as e:
        logger.error(f"Error parsing Towards Data Science page: {e}", exc_info=True) # Log completo del error

    return [] # Devolver lista vacía en caso de error

# --- Funciones de APIs Externas (Simplificadas) ---

async def fetch_news_from_newsapi(http_client: httpx.AsyncClient, query: str, page_size: int = 20) -> List[Dict]:
    # ... (mantener la lógica existente, asegurándose de manejar errores y devolver []) ...
    if not NEWSAPI_API_KEY: return []
    url = f"https://newsapi.org/v2/everything?q={query}&language=es&sortBy=publishedAt&pageSize={page_size}&apiKey={NEWSAPI_API_KEY}"
    try:
        response = await http_client.get(url, timeout=15.0)
        response.raise_for_status()
        data = response.json()
        logger.info(f"NewsAPI: Found {data.get('totalResults', 0)} articles for query '{query}'")
        return data.get('articles', [])
    except Exception as e:
        logger.error(f"Error fetching from NewsAPI: {e}")
        return []

async def fetch_news_from_gnews(http_client: httpx.AsyncClient, query: str, max_results: int = 10) -> List[Dict]:
    # ... (mantener la lógica existente, asegurándose de manejar errores y devolver []) ...
    if not GNEWS_API_KEY: return []
    url = f"https://gnews.io/api/v4/search?q={query}&lang=es&max={max_results}&token={GNEWS_API_KEY}"
    try:
        response = await http_client.get(url, timeout=15.0)
        response.raise_for_status()
        data = response.json()
        logger.info(f"GNews: Found {data.get('totalArticles', 0)} articles for query '{query}'")
        return data.get('articles', [])
    except Exception as e:
        logger.error(f"Error fetching from GNews: {e}")
        return []

async def fetch_news_from_mediastack(http_client: httpx.AsyncClient, query: str, limit: int = 10) -> List[Dict]:
     # ... (mantener la lógica existente, asegurándose de manejar errores y devolver []) ...
     if not MEDIASTACK_API_KEY: return []
     # Nota: Mediastack puede requerir 'keywords' en lugar de 'q' y tiene diferentes parámetros
     url = f"http://api.mediastack.com/v1/news?access_key={MEDIASTACK_API_KEY}&keywords={query}&languages=es&limit={limit}&sort=published_desc"
     try:
         response = await http_client.get(url, timeout=15.0)
         response.raise_for_status()
         data = response.json()
         logger.info(f"Mediastack: Found {len(data.get('data', []))} articles for query '{query}'")
         # Adaptar mapeo si es necesario (ej. 'url', 'image', 'published_at')
         return data.get('data', [])
     except Exception as e:
         logger.error(f"Error fetching from Mediastack: {e}")
         return []

# --- Funciones de Análisis --- #

def parse_json_from_gemini_response(text: str) -> Optional[Dict[str, Any]]:
    """Intenta extraer un bloque JSON del texto de respuesta de Gemini."""
    try:
        # Buscar el inicio y fin del bloque JSON, ignorando ```json``` si existe
        text_cleaned = text.strip().removeprefix('```json').removesuffix('```').strip()
        json_start = text_cleaned.find('{')
        json_end = text_cleaned.rfind('}')
        if json_start != -1 and json_end != -1:
            json_str = text_cleaned[json_start:json_end+1]
            return json.loads(json_str)
        else:
            print(f"Advertencia: No se encontró JSON en la respuesta de Gemini: {text}")
            return None
    except json.JSONDecodeError as e:
        print(f"Error decodificando JSON de Gemini: {e}. Respuesta: {text}")
        return None
    except Exception as e:
        print(f"Error inesperado parseando JSON de Gemini: {e}")
        return None

async def analyze_with_gemini(title: Optional[str], description: Optional[str]) -> Dict[str, Any]:
    """Analyzes news title and description using Gemini API."""
    if not settings.GEMINI_API_KEY or not title:
        return {} 
    
    content_to_analyze = f"Título: {title}"
    if description:
        # Limitar longitud de la descripción para no exceder límites de token
        content_to_analyze += f"\nResumen: {description[:1000]}" 
    else:
         content_to_analyze += "\nResumen: (No disponible)"

    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        prompt = f"""
        Analiza la siguiente noticia de tecnología/IA:
        {content_to_analyze}

        Devuelve SOLAMENTE un objeto JSON válido con las siguientes claves:
        - "relevance": Un número entero del 1 (poco relevante) al 10 (muy relevante) para un lector interesado en IA y tecnología.
        - "time_category": Clasifica la noticia como 'Hoy', 'Semana', 'Mes' o 'Antiguo' basado en su contenido y posible actualidad (no solo la fecha de publicación).
        - "sectors": Una lista de strings (máximo 5) con los sectores económicos o tecnológicos específicos mencionados o impactados (ej: ["Finanzas", "Robótica", "Cloud Computing", "Gaming"]). Si no aplica, devuelve lista vacía [].

        JSON:
        """
        response = await model.generate_content_async(prompt)
        analysis = parse_json_from_gemini_response(response.text)
        
        if analysis and isinstance(analysis, dict):
            return {
                "relevance_score": analysis.get("relevance"),
                "time_category": analysis.get("time_category"),
                "sectors": analysis.get("sectors", []) 
            }
        else:
             print(f"Análisis fallido para: {title}")
             return {}

    except Exception as e:
        print(f"Error llamando a Gemini API para '{title}': {e}")
        return {}

# --- Función Principal del Servicio --- #

async def fetch_and_store_news():
    """Fetches news from all sources and stores them in the database."""
    logger.info("Starting news aggregation task...")
    queries = [
        "inteligencia artificial generativa",
        "transformación digital empresas",
        "computación cuántica avances",
        "ciberseguridad ransomware",
        "modelos lenguaje grandes (LLM)",
        "automatización robótica procesos (RPA)",
        "blockchain finanzas",
        "tecnología salud IA",
        "gaming AAA lanzamiento",
        "hardware GPU IA",
        "cloud computing multicloud",
        "futuro del trabajo remoto IA",
        "impacto ético IA" # Consultas más específicas y de impacto
    ]
    all_raw_articles = []

    async with httpx.AsyncClient() as client:
        # 1. Fetch from APIs
        api_tasks = []
        for query in queries:
             # Limitar llamadas a APIs si es necesario para evitar cuotas
             api_tasks.append(fetch_news_from_newsapi(client, query, page_size=2)) # <-- Reducido a 2
             api_tasks.append(fetch_news_from_gnews(client, query, max_results=2)) # <-- Reducido a 2
             api_tasks.append(fetch_news_from_mediastack(client, query, limit=2)) # <-- Reducido a 2
        
        api_results = await asyncio.gather(*api_tasks, return_exceptions=True)
        
        for result in api_results:
            if isinstance(result, list):
                all_raw_articles.extend(result)
            elif isinstance(result, Exception):
                 logger.error(f"An API call failed: {result}")


        # 2. Scrape from Towards Data Science (DESACTIVADO TEMPORALMENTE)
        # scraped_articles = await scrape_towards_data_science(client)
        scraped_articles = [] # Devolver lista vacía para que el siguiente bucle no haga nada
        logger.info("Web scraping for Towards Data Science is temporarily disabled.")
        
        # 3. Process Scraped Articles (Check DB, Enrich, Create)
        async for db in get_db(): 
            processed_scraped_count = 0
            # Este bucle ahora no hará nada porque scraped_articles está vacío
            for article_data in scraped_articles:
                # url = article_data.get("url")
                # title = article_data.get("title")
                # if not url or not title:
                #     continue
                # 
                # existing_item = await crud_news.get_news_item_by_url(db, url)
                # if existing_item:
                #     continue
                # 
                # logger.info(f"Processing scraped article: {title[:50]}...")
                # enriched_data: Optional[Dict[str, Any]] = None
                # try:
                #     enriched_data = await enrich_news_with_gemini(
                #         title=title,
                #         url=url,
                #         description=None 
                #     )
                # except Exception as e:
                #      is_quota_error = isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 429
                #      log_level = logging.WARNING if is_quota_error else logging.ERROR
                #      error_type = "Quota limit likely reached" if is_quota_error else "Error"
                #      logger.log(log_level, f"{error_type} enriching article '{title[:50]}' with Gemini: {e}")
                #      continue 
                # 
                # if enriched_data:
                #     try:
                #         news_item_data = NewsItemCreate(
                #             title=enriched_data.get("title", title),
                #             description=enriched_data.get("description", "Descripción no generada."),
                #             url=url, 
                #             imageUrl=enriched_data.get("imageUrl"),
                #             publishedAt=enriched_data.get("publishedAt", datetime.now(timezone.utc)), 
                #             sourceName="Towards Data Science (Generado)",
                #             sourceId="towards-data-science", 
                #             relevance_score=enriched_data.get("relevance_score"),
                #             sectors=enriched_data.get("sectors", [])
                #         )
                #         await crud_news.create_news_item(db, news_item_data)
                #         processed_scraped_count += 1
                #         logger.info(f"Successfully enriched and stored: {news_item_data.title[:50]}...")
                #         await asyncio.sleep(0.5) 
                # 
                #     except Exception as e:
                #         logger.error(f"Error saving generated news item for '{title[:50]}': {e}", exc_info=True)
                pass # Mantener el pass para que el bucle for vacío sea válido

            logger.info(f"Processed and stored {processed_scraped_count} new articles from scraping (Currently 0 due to disabling).")


            # 4. Process API Articles (REACTIVANDO ENRIQUECIMIENTO GEMINI)
            processed_api_count = 0
            unique_api_urls = set() 

            for article in all_raw_articles:
                url = article.get('url')
                title = article.get('title')
                description = article.get('description') # Descripción original de la API
                
                if not url or not title or url in unique_api_urls:
                    continue

                unique_api_urls.add(url) 

                existing_item = await get_news_item_by_url(db, url)
                if existing_item:
                    continue
                
                logger.info(f"Processing API article: {title[:50]}...")

                # Intenta enriquecer con Gemini (maneja error de cuota)
                enriched_data: Optional[Dict[str, Any]] = None
                fallback_to_save = False # Flag para guardar sin enriquecer
                try:
                    enriched_data = await enrich_news_with_gemini(
                        title=title, 
                        url=url, 
                        description=description # Pasamos la descripción de la API
                    )
                except httpx.HTTPStatusError as e: # Capturar específicamente HTTPStatusError
                    if e.response.status_code == 429:
                         logger.warning(f"Quota limit likely reached enriching API article '{title[:50]}' with Gemini: {e}")
                         fallback_to_save = True # Marcar para guardar sin enriquecer
                         # NO continuar (continue), permitir que el flujo siga al bloque 'if' de abajo
                    else:
                         # Si es otro error HTTP, registrarlo y saltar la noticia
                         logger.error(f"HTTP Error {e.response.status_code} enriching API article '{title[:50]}' with Gemini: {e}")
                         continue # Saltar esta noticia
                except Exception as e: # Capturar cualquier otra excepción inesperada
                     logger.error(f"Unexpected error enriching API article '{title[:50]}' with Gemini: {e}", exc_info=True)
                     continue # Saltar esta noticia en caso de error no HTTP

                # Guardar si Gemini tuvo éxito O si falló por cuota (fallback)
                if enriched_data or fallback_to_save:
                    try:
                        # Mapeo cuidadoso de campos (varia por API!) + datos de Gemini si existen
                        published_at_str = article.get('publishedAt') or article.get('published_at') 
                        published_at_api = None
                        if published_at_str:
                           try:
                               published_at_api = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
                               if published_at_api.tzinfo is None:
                                   published_at_api = published_at_api.replace(tzinfo=timezone.utc)
                           except ValueError:
                                logger.warning(f"Could not parse API date: {published_at_str}")
                        
                        # Priorizar fecha de Gemini si existe, si no, la de la API, si no, ahora.
                        final_published_at = (enriched_data.get("publishedAt") if enriched_data else None) or published_at_api or datetime.now(timezone.utc)

                        # Priorizar imagen de Gemini si existe, si no, la de la API.
                        image_url_api = article.get('urlToImage') or article.get('image')
                        # Limpiar imageUrl si es "null" o vacío antes de asignar
                        image_url_gemini = enriched_data.get("imageUrl") if enriched_data else None
                        if isinstance(image_url_gemini, str) and (image_url_gemini.lower() == 'null' or not image_url_gemini.strip()):
                            image_url_gemini = None
                        final_image_url = image_url_gemini or image_url_api
                        
                        # Corregir obtención de sourceName/Id para manejar strings o dicts
                        source_info = article.get('source')
                        source_name_val = "Fuente Desconocida"
                        source_id_val = None
                        if isinstance(source_info, dict):
                            source_name_val = source_info.get('name', source_name_val)
                            source_id_val = source_info.get('id')
                        elif isinstance(source_info, str):
                            source_name_val = source_info # Usar el string directamente
                            # source_id_val ya es None por defecto
                        
                        # Crear el objeto NewsItemCreate con los datos procesados
                        news_item_data = NewsItemCreate(
                            title=(enriched_data.get("title", title) if enriched_data else title), 
                            description=(enriched_data.get("description", description) if enriched_data else description), 
                            url=url, 
                            imageUrl=final_image_url, 
                            publishedAt=final_published_at, 
                            sourceName=source_name_val + (" (Enriquecido)" if enriched_data else ""), 
                            sourceId=source_id_val, 
                            relevance_score=(enriched_data.get("relevance_score") if enriched_data else None), 
                            sectors=(enriched_data.get("sectors", []) if enriched_data else []) 
                        )
                        # Intentar guardar en la base de datos
                        await create_news_item(db, news_item_data)
                        processed_api_count += 1
                        log_msg = f"Successfully stored API article: {news_item_data.title[:50]}..." + (" (Enriched)" if enriched_data else " (Not Enriched - Quota?)")
                        logger.info(log_msg)
                        
                        await asyncio.sleep(2.0) # Pausa aumentada

                    except Exception as e:
                        # Asegurarse de que este except esté correctamente indentado
                        logger.error(f"Error saving processed API news item for '{title[:50]}': {e}", exc_info=True)
            
            # Log al final del procesamiento de APIs
            log_final = f"Processed and stored {processed_api_count} new articles from APIs."
            logger.info(log_final)

    # Log al final de toda la tarea
    logger.info("News aggregation task finished.")

# --- Programación (Si usas APScheduler) ---
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# scheduler = AsyncIOScheduler(timezone="Europe/Madrid") # O tu zona horaria
# scheduler.add_job(fetch_and_store_news, 'interval', hours=4) # Ejecutar cada 4 horas
# # Iniciar scheduler en el lifespan de FastAPI o en un script separado
# # scheduler.start()

# --- Fin del archivo ---