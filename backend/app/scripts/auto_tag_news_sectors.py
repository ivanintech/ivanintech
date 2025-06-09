import asyncio
import json
import logging
from typing import List, Optional, cast

import google.generativeai as genai
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func # For func.json_length or similar if needed
from sqlalchemy import JSON

from app.core.config import settings
from app.db.session import AsyncSessionLocal, async_engine # Added async_engine for potential direct use if needed
from app.db.models.news_item import NewsItem # Import NewsItem model
from app.db.base import Base # To create tables if script is run standalone for the first time (optional)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure Gemini API Key
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    logger.info("Gemini API Key configurada.")
else:
    logger.warning("GEMINI_API_KEY no está configurada. El script no podrá obtener sectores de la IA.")

async def get_sectors_from_gemini(title: str, description: Optional[str]) -> List[str]:
    """
    Obtiene una lista de sectores relevantes para una noticia utilizando Gemini.
    """
    if not settings.GEMINI_API_KEY:
        logger.error("No se puede llamar a Gemini: API key no configurada.")
        return []

    model = genai.GenerativeModel("gemini-1.5-flash-latest") # Using the same model as gemini_service

    prompt_parts = [
        "Eres un asistente experto en categorización de noticias tecnológicas.",
        "Analiza el siguiente título y descripción de una noticia y devuelve una lista de hasta 5 sectores tecnológicos clave a los que pertenece.",
        "Sectores comunes podrían ser: 'Inteligencia Artificial', 'Cloud Computing', 'Ciberseguridad', 'Desarrollo de Software', 'Hardware', 'Gaming', 'Mobile', 'Startups', 'eCommerce', 'Fintech', 'EdTech', 'HealthTech', 'Blockchain', 'Sostenibilidad Tecnológica', 'IoT', 'Big Data', 'Realidad Virtual/Aumentada'.",
        "Si no estás seguro o no aplica, devuelve una lista vacía.",
        "Devuelve ÚNICAMENTE un objeto JSON que sea una lista de strings. Por ejemplo: [\"IA\", \"Cloud\"] o [].",
        "No incluyas explicaciones adicionales, solo el JSON.",
        "---",
        f"Título: {title}",
    ]
    if description:
        prompt_parts.append(f"Descripción: {description[:1000]}") # Limitar longitud de descripción
    prompt_parts.append("---")
    prompt_parts.append("Lista de sectores (JSON):")
    
    complete_prompt = "\n".join(prompt_parts)

    try:
        # logger.debug(f"Prompt para Gemini:\n{complete_prompt}")
        response = await model.generate_content_async(complete_prompt)
        
        cleaned_response_text = response.text.strip()
        # logger.debug(f"Respuesta de Gemini (raw): {cleaned_response_text}")

        if cleaned_response_text.startswith("```json"):
            cleaned_response_text = cleaned_response_text[7:]
        if cleaned_response_text.endswith("```"):
            cleaned_response_text = cleaned_response_text[:-3]
        
        cleaned_response_text = cleaned_response_text.strip() # Asegurar que no haya espacios extra
        
        # Intento de parsear. Si es solo una lista vacía '[]', puede no ser detectado por los ```json```
        if not cleaned_response_text: # Si después de limpiar queda vacío, asumir lista vacía
             logger.warning(f"Gemini devolvió una respuesta vacía para '{title}'. Asumiendo [].")
             return []

        sectors = json.loads(cleaned_response_text)
        if isinstance(sectors, list) and all(isinstance(s, str) for s in sectors):
            logger.info(f"Sectores obtenidos para '{title}': {sectors}")
            return sectors
        else:
            logger.warning(f"Respuesta de Gemini no fue una lista de strings para '{title}': {sectors}. Se devolvió: {cleaned_response_text}")
            return []
    except json.JSONDecodeError:
        logger.error(f"Error decodificando JSON de Gemini para '{title}'. Respuesta: \n{response.text}", exc_info=True)
        return []
    except Exception as e:
        logger.error(f"Error llamando a la API de Gemini para '{title}': {e}", exc_info=True)
        return []

async def auto_tag_news_sectors(db: AsyncSession, limit: Optional[int] = None):
    """
    Recorre las noticias sin sectores y les asigna sectores usando Gemini.
    """
    logger.info("Iniciando el proceso de auto-etiquetado de sectores para noticias.")
    
    # SQLAlchemy no tiene un tipo JSON list nativo simple para SQLite.
    # Usamos `None` para nuevos y `cast([], JSON)` para listas vacías existentes.
    # El `cast([], JSON)` es más para PostgreSQL o MySQL.
    # Para SQLite, podríamos necesitar `NewsItem.sectors.astext == '[]'` o similar, o filtrar en Python.
    # Por ahora, nos enfocamos en `sectors IS NULL` y el filtrado de `[]` en Python para simplicidad.
    # O mejor aún, usar func.json_type o func.json_array_length si la base de datos lo soporta (ej. PostgreSQL).
    # Para SQLite, `NewsItem.sectors == json.dumps([])` podría funcionar si se guardan como strings.
    # O `NewsItem.sectors == []` si SQLAlchemy lo mapea correctamente.
    # Dado que NewsItem.sectors es Mapped[Optional[List[str]]] = mapped_column(JSON..),
    # SQLAlchemy debería manejar `[]` correctamente en la comparación si el dialecto lo soporta.
    # La forma más segura es NewsItem.sectors == None y luego un json_array_length si es pg, o filtrar en python.

    stmt = select(NewsItem)

    if limit:
        stmt = stmt.limit(limit)

    result = await db.execute(stmt)
    news_items_to_process = result.scalars().all()
    
    # Filtrado adicional en Python para `[]` si la consulta SQL no es robusta para todos los casos
    filtered_items = []
    for item in news_items_to_process:
        if item.sectors is None or item.sectors == []:
            filtered_items.append(item)
    news_items_to_process = filtered_items

    if not news_items_to_process:
        logger.info("No se encontraron noticias que necesiten etiquetado de sectores.")
        return

    logger.info(f"Se encontraron {len(news_items_to_process)} noticias para procesar.")
    
    processed_count = 0
    updated_count = 0

    for news_item in news_items_to_process:
        logger.info(f"Procesando noticia ID: {news_item.id}, Título: {news_item.title}")
        
        # Prevenir re-procesamiento si ya tiene sectores (doble chequeo)
        if news_item.sectors and len(news_item.sectors) > 0:
            logger.info(f"Saltando noticia ID: {news_item.id}, ya tiene sectores: {news_item.sectors}")
            continue

        sectors = await get_sectors_from_gemini(news_item.title, news_item.description)
        
        if sectors: # Solo actualizar si Gemini devuelve algo
            news_item.sectors = sectors
            db.add(news_item)
            updated_count += 1
            logger.info(f"Noticia ID: {news_item.id} actualizada con sectores: {sectors}")
        else:
            # Opcional: Marcar como procesado para no reintentar indefinidamente si Gemini consistentemente no devuelve nada.
            # Por ahora, simplemente no lo actualizamos y se reintentará la próxima vez.
            # O podemos ponerle una lista vacía explícitamente si queremos marcarlo como "intentado pero sin resultado".
            # De acuerdo al plan, si no hay sectores, se guarda la lista vacía.
            # La función get_sectors_from_gemini ya devuelve [] en caso de error o si no hay sectores.
            # Así que si `sectors` está vacío aquí, es porque Gemini devolvió [] o hubo un error.
            # Si queremos que `[]` se guarde para indicar "procesado, sin sectores encontrados", debemos hacerlo explícito.
            # Por ahora, si `sectors` es [], no se actualiza (a menos que fuera `None` antes).
            # Si queremos que `sectors` quede `[]` explícitamente después de procesar y no encontrar nada:
            if news_item.sectors is None: # Si era None y Gemini no encontró nada (devuelve [])
                news_item.sectors = [] # Establecer a lista vacía
                db.add(news_item)
                logger.info(f"Noticia ID: {news_item.id} marcada con sectores vacíos []." )
            else: # Si ya era [] y Gemini no encontró nada, no hay cambio.
                logger.info(f"No se encontraron sectores para la noticia ID: {news_item.id} o ya estaba vacía.")


        processed_count += 1
        if processed_count % 20 == 0: # Commit cada 20 noticias
            logger.info(f"Procesadas {processed_count} noticias. Haciendo commit parcial...")
            await db.commit()
            logger.info("Commit parcial realizado.")

        # >>> AÑADIR RETRASO AQUÍ <<<
        if settings.GEMINI_API_KEY: # Solo pausar si estamos usando la API
            logger.debug(f"Esperando 5 segundos antes de la siguiente solicitud a Gemini...")
            await asyncio.sleep(5) # Pausa de 5 segundos

    if processed_count > 0 : # Commit final si hubo procesados
        logger.info("Proceso finalizado. Haciendo commit final...")
        await db.commit()
        logger.info(f"Commit final realizado. Total noticias procesadas: {processed_count}. Total noticias actualizadas con nuevos sectores: {updated_count}.")
    else:
        logger.info("No se procesaron noticias en esta ejecución.")


async def main(run_limit: Optional[int] = None):
    """
    Función principal para ejecutar el script.
    """
    # Opcional: Crear tablas si no existen (generalmente manejado por Alembic, pero útil para scripts standalone)
    # async with async_engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    #     logger.info("Tablas (si no existían) verificadas/creadas.")

    async with AsyncSessionLocal() as session:
        await auto_tag_news_sectors(session, limit=run_limit)

if __name__ == "__main__":
    # Permitir pasar un límite desde la línea de comandos, ej: python auto_tag_news_sectors.py 10
    limit_arg = None
    import sys
    if len(sys.argv) > 1:
        try:
            limit_arg = int(sys.argv[1])
            logger.info(f"Ejecutando script con un límite de {limit_arg} noticias.")
        except ValueError:
            logger.warning(f"Argumento '{sys.argv[1]}' no es un número válido para el límite. Ejecutando sin límite.")
            
    asyncio.run(main(run_limit=limit_arg)) 