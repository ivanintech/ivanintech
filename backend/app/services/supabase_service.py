"""
Servicio para manejar la API REST de Supabase
Alternativa a la conexión PostgreSQL directa cuando esta está bloqueada
"""

import httpx
import logging
from typing import List, Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class SupabaseService:
    """Servicio para interactuar con la API REST de Supabase"""
    
    def __init__(self):
        self.base_url = settings.SUPABASE_URL
        self.service_key = settings.SUPABASE_SERVICE_KEY
        self.headers = {
            "apikey": self.service_key,
            "Authorization": f"Bearer {self.service_key}",
            "Content-Type": "application/json"
        }
    
    async def get_projects(self) -> List[Dict[str, Any]]:
        """Obtiene todos los proyectos desde Supabase"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/rest/v1/projects?select=*",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    projects = response.json()
                    logger.info(f"Obtenidos {len(projects)} proyectos desde Supabase API")
                    return projects
                else:
                    logger.error(f"Error obteniendo proyectos: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error en get_projects: {e}")
            return []
    
    async def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un proyecto específico por ID"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/rest/v1/projects?id=eq.{project_id}&select=*",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    projects = response.json()
                    return projects[0] if projects else None
                else:
                    logger.error(f"Error obteniendo proyecto {project_id}: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error en get_project: {e}")
            return None
    
    async def create_project(self, project_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crea un nuevo proyecto"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/rest/v1/projects",
                    headers=self.headers,
                    json=project_data
                )
                
                if response.status_code == 201:
                    logger.info(f"Proyecto creado exitosamente")
                    return response.json()[0] if response.json() else project_data
                else:
                    logger.error(f"Error creando proyecto: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error en create_project: {e}")
            return None
    
    async def update_project(self, project_id: str, project_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Actualiza un proyecto existente"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/rest/v1/projects?id=eq.{project_id}",
                    headers=self.headers,
                    json=project_data
                )
                
                if response.status_code == 200:
                    logger.info(f"Proyecto {project_id} actualizado exitosamente")
                    return response.json()[0] if response.json() else project_data
                else:
                    logger.error(f"Error actualizando proyecto: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error en update_project: {e}")
            return None
    
    async def delete_project(self, project_id: str) -> bool:
        """Elimina un proyecto"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}/rest/v1/projects?id=eq.{project_id}",
                    headers=self.headers
                )
                
                if response.status_code == 204:
                    logger.info(f"Proyecto {project_id} eliminado exitosamente")
                    return True
                else:
                    logger.error(f"Error eliminando proyecto: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error en delete_project: {e}")
            return False
    
    async def get_featured_projects(self) -> List[Dict[str, Any]]:
        """Obtiene solo los proyectos destacados"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/rest/v1/projects?is_featured=eq.true&select=*",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    projects = response.json()
                    logger.info(f"Obtenidos {len(projects)} proyectos destacados")
                    return projects
                else:
                    logger.error(f"Error obteniendo proyectos destacados: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error en get_featured_projects: {e}")
            return []
    
    async def test_connection(self) -> bool:
        """Prueba la conexión con Supabase"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/rest/v1/projects?select=id&limit=1",
                    headers=self.headers
                )
                
                return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Error en test_connection: {e}")
            return False

    # === BLOG POSTS METHODS ===
    
    async def get_blog_posts(self, limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """Obtiene blog posts publicados desde Supabase"""
        try:
            async with httpx.AsyncClient() as client:
                # Filtrar solo por status=published y ordenar por fecha descendente
                query = (
                    f"{self.base_url}/rest/v1/blog_posts"
                    f"?select=*&limit={limit}&offset={skip}&status=eq.published&order=published_date.desc"
                )
                response = await client.get(query, headers=self.headers)
                if response.status_code == 200:
                    posts = response.json()
                    # Agregar campo author a cada post (mantener si ya estaba)
                    for post in posts:
                        post['author'] = {
                            'id': post.get('author_id', 1),
                            'full_name': 'Ivan'
                        }
                    logger.info(f"Obtenidos {len(posts)} blog posts publicados desde Supabase API")
                    return posts
                else:
                    logger.error(f"Error obteniendo blog posts: {response.status_code} - {response.text}")
                    return []
        except Exception as e:
            logger.error(f"Error en get_blog_posts: {e}")
            return []
    
    async def get_blog_post_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Obtiene un blog post específico por slug"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/rest/v1/blog_posts?slug=eq.{slug}&select=*",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    posts = response.json()
                    if posts:
                        post = posts[0]
                        # Agregar campo author
                        post['author'] = {
                            'id': post.get('author_id', 1),
                            'full_name': 'Ivan'
                        }
                        return post
                    return None
                else:
                    logger.error(f"Error obteniendo blog post {slug}: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error en get_blog_post_by_slug: {e}")
            return None

    async def create_blog_post(self, blog_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crea un nuevo blog post en Supabase"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/rest/v1/blog_posts",
                    headers=self.headers,
                    json=blog_data
                )
                
                if response.status_code == 201:
                    created_post = response.json()
                    logger.info(f"Blog post creado exitosamente en Supabase: {blog_data.get('title')}")
                    return created_post[0] if created_post else blog_data
                else:
                    logger.error(f"Error creando blog post: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error en create_blog_post: {e}")
            return None

    async def update_blog_post(self, post_id: str, blog_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Actualiza un blog post existente en Supabase"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/rest/v1/blog_posts?id=eq.{post_id}",
                    headers=self.headers,
                    json=blog_data
                )
                
                if response.status_code == 200:
                    logger.info(f"Blog post {post_id} actualizado exitosamente en Supabase")
                    return response.json()[0] if response.json() else blog_data
                else:
                    logger.error(f"Error actualizando blog post: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error en update_blog_post: {e}")
            return None

    async def delete_blog_post(self, post_id: str) -> bool:
        """Elimina un blog post de Supabase"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}/rest/v1/blog_posts?id=eq.{post_id}",
                    headers=self.headers
                )
                
                if response.status_code == 204:
                    logger.info(f"Blog post {post_id} eliminado exitosamente de Supabase")
                    return True
                else:
                    logger.error(f"Error eliminando blog post: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error en delete_blog_post: {e}")
            return False

    # === NEWS METHODS ===
    
    async def get_news(self, limit: int = 10, skip: int = 0) -> List[Dict[str, Any]]:
        """Obtiene noticias desde Supabase"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/rest/v1/news_items?select=*&limit={limit}&offset={skip}&order=publishedAt.desc",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    news = response.json()
                    logger.info(f"Obtenidas {len(news)} noticias desde Supabase API")
                    return news
                else:
                    logger.error(f"Error obteniendo noticias: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error en get_news: {e}")
            return []

    async def create_news_item(self, news_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crea una nueva noticia en Supabase"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/rest/v1/news_items",
                    headers=self.headers,
                    json=news_data
                )
                
                if response.status_code == 201:
                    created_news = response.json()
                    logger.info(f"Noticia creada exitosamente en Supabase: {news_data.get('title')}")
                    return created_news[0] if created_news else news_data
                else:
                    logger.error(f"Error creando noticia: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error en create_news_item: {e}")
            return None

    async def bulk_create_news(self, news_list: List[Dict[str, Any]]) -> int:
        """Crea múltiples noticias en Supabase de una vez"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/rest/v1/news_items",
                    headers=self.headers,
                    json=news_list
                )
                
                if response.status_code == 201:
                    created_count = len(news_list)
                    logger.info(f"Creadas {created_count} noticias exitosamente en Supabase")
                    return created_count
                else:
                    logger.error(f"Error creando noticias en bulk: {response.status_code} - {response.text}")
                    return 0
                    
        except Exception as e:
            logger.error(f"Error en bulk_create_news: {e}")
            return 0

    # === RESOURCE LINKS METHODS ===
    
    async def get_resource_links(self, limit: int = 100, skip: int = 0, resource_type: str = None, tags: List[str] = None) -> List[Dict[str, Any]]:
        """Obtiene resource links desde Supabase"""
        try:
            async with httpx.AsyncClient() as client:
                # Construir query con filtros
                query = f"{self.base_url}/rest/v1/resource_links?select=*&limit={limit}&offset={skip}&order=created_at.desc"
                
                # Filtro por tipo de recurso
                if resource_type:
                    query += f"&resource_type=eq.{resource_type}"
                
                # Filtro por tags (búsqueda parcial)
                if tags:
                    for tag in tags:
                        query += f"&tags=ilike.%{tag}%"
                
                response = await client.get(query, headers=self.headers)
                
                if response.status_code == 200:
                    resources = response.json()
                    logger.info(f"Obtenidos {len(resources)} resource links desde Supabase API")
                    return resources
                else:
                    logger.error(f"Error obteniendo resource links: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error en get_resource_links: {e}")
            return []
    
    async def get_resource_link(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un resource link específico por ID"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/rest/v1/resource_links?id=eq.{resource_id}&select=*",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    resources = response.json()
                    return resources[0] if resources else None
                else:
                    logger.error(f"Error obteniendo resource link {resource_id}: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error en get_resource_link: {e}")
            return None

    async def create_resource_link(self, resource_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crea un nuevo resource link en Supabase"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/rest/v1/resource_links",
                    headers=self.headers,
                    json=resource_data
                )
                
                if response.status_code == 201:
                    created_resource = response.json()
                    logger.info(f"Resource link creado exitosamente en Supabase: {resource_data.get('title')}")
                    return created_resource[0] if created_resource else resource_data
                else:
                    logger.error(f"Error creando resource link: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error en create_resource_link: {e}")
            return None

    async def update_resource_link(self, resource_id: str, resource_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Actualiza un resource link existente en Supabase"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/rest/v1/resource_links?id=eq.{resource_id}",
                    headers=self.headers,
                    json=resource_data
                )
                
                if response.status_code == 200:
                    logger.info(f"Resource link {resource_id} actualizado exitosamente en Supabase")
                    return response.json()[0] if response.json() else resource_data
                else:
                    logger.error(f"Error actualizando resource link: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error en update_resource_link: {e}")
            return None

    async def delete_resource_link(self, resource_id: str) -> bool:
        """Elimina un resource link de Supabase"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}/rest/v1/resource_links?id=eq.{resource_id}",
                    headers=self.headers
                )
                
                if response.status_code == 204:
                    logger.info(f"Resource link {resource_id} eliminado exitosamente de Supabase")
                    return True
                else:
                    logger.error(f"Error eliminando resource link: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error en delete_resource_link: {e}")
            return False

# Instancia global del servicio
supabase_service = SupabaseService() 