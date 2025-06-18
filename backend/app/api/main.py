from fastapi import APIRouter

from app.api.routes import login, utils, users, projects
from app.api.routes import blog
from app.api.routes import news
from app.api.routes import contact
from app.api.routes import resource_links
from app.api.routes import home
from app.core.config import settings

api_router = APIRouter()

@api_router.get("/health", status_code=200)
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}

api_router.include_router(login.router)
api_router.include_router(utils.router)
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(blog.router, prefix="/blog", tags=["blog"])
api_router.include_router(news.router, prefix="/news", tags=["news"])
api_router.include_router(contact.router, prefix="/contact", tags=["contact"])
api_router.include_router(resource_links.router, prefix="/resource-links", tags=["resource-links"])
api_router.include_router(home.router)


if settings.ENVIRONMENT == "local":
    pass
