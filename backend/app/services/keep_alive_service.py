"""
Servicio de Keep-Alive para mantener la aplicación activa en Render.
Evita que la aplicación entre en reposo y mejora los tiempos de respuesta.
"""

import asyncio
import logging
import aiohttp
from datetime import datetime, timezone
from typing import Optional
import os

logger = logging.getLogger(__name__)

class KeepAliveService:
    """Servicio para mantener la aplicación activa en Render."""
    
    def __init__(self, app_url: str, interval_minutes: int = 15):
        self.app_url = app_url
        self.interval_minutes = interval_minutes
        self.is_running = False
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def start(self):
        """Inicia el servicio de keep-alive."""
        if self.is_running:
            logger.warning("Keep-alive service already running")
            return
        
        self.is_running = True
        self.session = aiohttp.ClientSession()
        
        logger.info(f"🚀 Keep-alive service started for {self.app_url}")
        logger.info(f"   Interval: {self.interval_minutes} minutes")
        
        try:
            while self.is_running:
                await self._ping_app()
                await asyncio.sleep(self.interval_minutes * 60)
        except Exception as e:
            logger.error(f"Error in keep-alive service: {e}")
        finally:
            if self.session:
                await self.session.close()
    
    async def stop(self):
        """Detiene el servicio de keep-alive."""
        self.is_running = False
        logger.info("🛑 Keep-alive service stopped")
    
    async def _ping_app(self):
        """Realiza un ping a la aplicación."""
        try:
            if not self.session:
                return
            
            start_time = datetime.now(timezone.utc)
            
            # Intentar ping al endpoint de health
            health_url = f"{self.app_url}/health"
            async with self.session.get(health_url, timeout=10) as response:
                if response.status == 200:
                    response_time = (datetime.now(timezone.utc) - start_time).total_seconds()
                    logger.info(f"✅ Keep-alive ping successful: {response_time:.2f}s")
                else:
                    logger.warning(f"⚠️ Keep-alive ping failed: HTTP {response.status}")
                    
        except asyncio.TimeoutError:
            logger.warning("⚠️ Keep-alive ping timeout")
        except Exception as e:
            logger.error(f"❌ Keep-alive ping error: {e}")

# Instancia global del servicio
keep_alive_service: Optional[KeepAliveService] = None

async def start_keep_alive_service():
    """Inicia el servicio de keep-alive globalmente."""
    global keep_alive_service
    
    # Solo iniciar en producción (Render)
    if os.getenv("ENVIRONMENT") == "production":
        app_url = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("SERVER_HOST", "http://localhost:8000")
        
        keep_alive_service = KeepAliveService(app_url)
        asyncio.create_task(keep_alive_service.start())
        logger.info("🌐 Keep-alive service configured for production")

async def stop_keep_alive_service():
    """Detiene el servicio de keep-alive globalmente."""
    global keep_alive_service
    
    if keep_alive_service:
        await keep_alive_service.stop()
        keep_alive_service = None
